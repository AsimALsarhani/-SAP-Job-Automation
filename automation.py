import os
import time
import logging
import smtplib
import tempfile
from email.message import EmailMessage
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Environment variable configuration (set these in GitHub secrets)
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")
SAP_URL = os.environ.get("SAP_URL")  # Must be set as a secret

if not SAP_URL:
    raise Exception("SAP_URL is not provided. Please set the SAP_URL environment variable.")

# Email SMTP configuration (Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def initialize_browser():
    """
    Initialize the Chrome WebDriver with a unique user data directory.
    """
    user_data_dir = tempfile.mkdtemp()
    options = Options()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--headless")  # Remove if you want to see the browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    logging.info(f"Browser initialized with user data directory: {user_data_dir}")
    return driver

def access_url_with_retry(driver, url, max_attempts=3, delay=5):
    """
    Attempts to access the given URL with retry logic.
    Verifies document.readyState is complete and that the login field (ID 'username') is present.
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            logging.info(f"Attempt {attempt + 1}: accessing {url}")
            driver.get(url)
            time.sleep(3)
            ready_state = driver.execute_script("return document.readyState")
            logging.info(f"Document ready state: {ready_state}")
            if ready_state == "complete" and driver.find_elements(By.ID, "username"):
                logging.info("Page loaded successfully; login field found.")
                return True
            else:
                logging.info("Page not fully loaded or login field missing.")
        except WebDriverException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
        attempt += 1
        time.sleep(delay)
    return False

def perform_login(driver):
    """
    Performs login actions on the SAP login page.
    Assumes the page is loaded.
    """
    try:
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(SAP_USERNAME)
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(SAP_PASSWORD)
        
        # Wait for and click the "Sign In" button (assumed to have ID 'signIn')
        sign_in_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "signIn"))
        )
        sign_in_button.click()
        logging.info("Login action performed successfully.")
        
        # Wait for a post-login element (adjust selector as needed)
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "mainDashboard"))
        )
        logging.info("Post-login dashboard loaded successfully.")
    except Exception as e:
        logging.error(f"Login failed: {e}")
        raise Exception("Login failed") from e

def send_email_with_screenshot(screenshot_path):
    """
    Sends an email with the given screenshot attached.
    """
    try:
        msg = EmailMessage()
        msg["Subject"] = "SAP Job Automation - Screenshot"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content("Attached is the screenshot from SAP Job Automation.")
        
        with open(screenshot_path, "rb") as f:
            img_data = f.read()
        msg.add_attachment(img_data, maintype="image", subtype="png", filename="screenshot.png")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Sending email failed: {e}")
        raise

def main():
    driver = None
    try:
        driver = initialize_browser()
        if not access_url_with_retry(driver, SAP_URL):
            raise Exception("Failed to access SAP URL after multiple attempts.")
        
        perform_login(driver)
        
        # Capture screenshot after login
        screenshot_path = "screenshot.png"
        time.sleep(5)  # Allow dynamic content to load
        driver.save_screenshot(screenshot_path)
        logging.info("Screenshot captured.")
        
        send_email_with_screenshot(screenshot_path)
    except Exception as e:
        logging.error(f"Main execution failed: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Browser terminated.")

if __name__ == "__main__":
    main()
