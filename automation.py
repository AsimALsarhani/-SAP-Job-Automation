import os
import time
import logging
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.common import WebDriverException, TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

# Environment variable configuration (set these in GitHub secrets)
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")
SAP_URL = os.environ.get("SAP_URL")

# Validate mandatory environment variables
if not SAP_URL:
    raise EnvironmentError("SAP_URL environment variable is required")

# Constants
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MAX_RETRIES = 3
RETRY_DELAY = 5

def configure_browser():
    """Configure Chrome options and service"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def safe_send_keys(element, text, max_retries=3):
    """Retry sending keys with stale element handling"""
    for attempt in range(max_retries):
        try:
            element.clear()
            element.send_keys(text)
            return True
        except StaleElementReferenceException:
            logging.warning(f"Stale element on send keys attempt {attempt+1}")
            time.sleep(2)
    return False

def find_clickable_element(selector, timeout=30):
    """Generic function to find clickable elements with retries"""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(selector)
    )

def send_email(screenshot_path):
    """Send notification email with attachment"""
    try:
        msg = EmailMessage()
        msg["Subject"] = "SAP Automation Report - Success"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content("SAP automation completed successfully.\nAttached: Latest status screenshot.")

        with open(screenshot_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="image", subtype="png", filename="status.png")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        logging.info("Notification email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

def main():
    global driver
    driver = None
    try:
        driver = configure_browser()
        logging.info("Browser configured successfully")

        # Load SAP URL with retries
        for attempt in range(MAX_RETRIES):
            try:
                driver.get(SAP_URL)
                WebDriverWait(driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == 'complete'
                )
                if driver.find_elements(By.ID, "username"):
                    logging.info("Login page loaded successfully")
                    break
            except WebDriverException as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                logging.warning(f"Page load failed attempt {attempt+1}: {str(e)}")
                time.sleep(RETRY_DELAY)

        # Login process
        username = find_clickable_element((By.ID, "username"))
        safe_send_keys(username, SAP_USERNAME)
        
        password = find_clickable_element((By.ID, "password"))
        safe_send_keys(password, SAP_PASSWORD)

        # Smart sign-in button detection
        sign_in_selector = (By.XPATH, 
            "//*[contains(translate(., 'SIGNIN', 'signin'), 'sign in')]")
        sign_in_button = find_clickable_element(sign_in_selector, 45)
        sign_in_button.click()
        logging.info("Login credentials submitted")

        # Post-login verification
        WebDriverWait(driver, 90).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@id, 'main') or contains(@class, 'dashboard')][contains(translate(., 'DASHBOARD', 'dashboard'), 'dashboard')]"
            ))
        )
        logging.info("Dashboard loaded successfully")

        # Save operation
        save_button = find_clickable_element((
            By.XPATH,
            "//button[contains(translate(., 'SAVE', 'save'), 'save')]"
        ), 30)
        save_button.click()
        logging.info("Save action performed")

        # Capture verification
        time.sleep(3)  # Allow save confirmation to appear
        status_element = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH,
                "//*[contains(@id, 'lastSave') or contains(text(), 'Last update')]"))
        )
        ActionChains(driver).move_to_element(status_element).perform()
        
        screenshot_path = "sap_status.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Screenshot saved to {screenshot_path}")

        # Send notification
        send_email(screenshot_path)
        logging.info("Automation completed successfully")

    except Exception as e:
        logging.error(f"Automation failed: {str(e)}")
        if driver:
            driver.save_screenshot("error_screenshot.png")
            logging.info("Saved error screenshot to error_screenshot.png")
        raise

    finally:
        if driver:
            driver.quit()
            logging.info("Browser closed properly")

if __name__ == "__main__":
    main()
