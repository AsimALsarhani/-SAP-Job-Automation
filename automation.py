import os
import time
import logging
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Environment Configuration
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")
SAP_URL = os.environ.get("SAP_URL")  # Mandatory

# Validation Checks
if not SAP_URL:
    raise ValueError("SAP_URL environment variable must be set")
if not all(["@" in email for email in [SENDER_EMAIL, RECIPIENT_EMAIL]]):
    raise ValueError("Invalid email configuration")

# Email Settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def initialize_browser():
    """Configure Chrome with optimal headless settings"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-gpu")
    
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def perform_login(driver):
    """Execute login with robust error handling"""
    try:
        # Username Entry
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(SAP_USERNAME)
        
        # Password Entry
        driver.find_element(By.ID, "password").send_keys(SAP_PASSWORD)
        
        # Login Button
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "signIn"))
        ).click()
        
        # Post-Login Verification
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sap-main-content"))
        )
        logging.info("Login successful")
        
    except (TimeoutException, NoSuchElementException) as e:
        logging.error(f"Login failure: {str(e)}")
        driver.save_screenshot("login_failure.png")
        raise

def send_report(screenshot_path):
    """Send email with attachment"""
    try:
        msg = EmailMessage()
        msg["Subject"] = "SAP Automation Result"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content("Process completed. See attached report.")
        
        with open(screenshot_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="image", subtype="png", filename="report.png")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        logging.info("Email dispatched successfully")
        
    except smtplib.SMTPException as e:
        logging.error(f"Email failure: {str(e)}")
        raise

def main_execution():
    """Main workflow controller"""
    driver = None
    try:
        driver = initialize_browser()
        logging.info(f"Navigating to SAP portal: {SAP_URL}")
        driver.get(SAP_URL)
        
        perform_login(driver)
        
        # Capture Evidence
        time.sleep(3)  # Stabilization
        screenshot_path = "success_report.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Screenshot captured: {screenshot_path}")
        
        send_report(screenshot_path)
        
    except Exception as e:
        logging.error(f"Critical failure: {str(e)}", exc_info=True)
        if driver:
            driver.save_screenshot("critical_error.png")
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Browser terminated")

if __name__ == "__main__":
    main_execution()
