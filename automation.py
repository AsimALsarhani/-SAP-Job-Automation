import os
import time
import logging
from logging.handlers import RotatingFileHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import smtplib

# Configure logging with rotation
log_handler = RotatingFileHandler("selenium_debug.log", maxBytes=5 * 1024 * 1024, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.ERROR)

# Retrieve credentials from environment variables
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = "asimalsarhani@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(subject, body, screenshot_path=None):
    """Send an email with optional screenshot attachment."""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    
    msg.attach(MIMEText(body, "plain"))
    
    if screenshot_path:
        with open(screenshot_path, "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header("Content-Disposition", "attachment", filename=os.path.basename(screenshot_path))
            msg.attach(img)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        logging.info(f"Email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def initialize_webdriver():
    """Initialize the Chrome WebDriver with options."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--headless")
    
    unique_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={unique_dir}")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def sign_in(driver):
    """Sign in to the SAP portal."""
    try:
        SAP_SIGNIN_URL = f"https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05"
        driver.get(SAP_SIGNIN_URL)
        logging.info("Navigating to SAP sign-in page...")

        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, "username")))
        
        driver.find_element(By.NAME, "username").send_keys(SAP_USERNAME)
        driver.find_element(By.NAME, "password").send_keys(SAP_PASSWORD)
        driver.find_element(By.XPATH, "//button[@data-testid='signInButton']").click()
        
        WebDriverWait(driver, 60).until(EC.url_changes(SAP_SIGNIN_URL))
        driver.save_screenshot("login_success.png")
        logging.info("Login successful.")
    except Exception as e:
        driver.save_screenshot("login_failed.png")
        send_email("SAP Login Failed", f"Error: {e}", "login_failed.png")
        logging.error(f"Login failed: {e}")
        raise

def click_save_button(driver):
    """Click the save button and handle potential errors."""
    try:
        save_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='saveButton']"))
        )
        save_button.click()
        driver.save_screenshot("save_clicked.png")
        logging.info("Save button clicked.")
    except Exception as e:
        driver.save_screenshot("save_failed.png")
        send_email("Save Button Click Failed", f"Error: {e}", "save_failed.png")
        logging.error(f"Save button error: {e}")
        raise

def main():
    driver = initialize_webdriver()
    try:
        sign_in(driver)
        click_save_button(driver)
    except Exception as e:
        logging.error(f"Script encountered an error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
