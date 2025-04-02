import os
import time
import logging
import smtplib
import tempfile
from email.message import EmailMessage
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
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

# Validate mandatory SAP_URL
if not SAP_URL or SAP_URL == "your-sap-url":
    raise ValueError("SAP_URL environment variable must be set and valid")

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def initialize_driver():
    """Initialize Chrome WebDriver with enhanced options"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def handle_login(driver):
    """Handle SAP login process with improved reliability"""
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(SAP_USERNAME)
        
        driver.find_element(By.ID, "password").send_keys(SAP_PASSWORD)
        
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "signIn"))
        ).click()
        
        # Verify successful login
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sap-main-content"))
        logging.info("Login successful")
    except (TimeoutException, NoSuchElementException) as e:
        logging.error(f"Login failed: {str(e)}")
        raise

def send_email_notification(screenshot_path):
    """Send email with enhanced error handling"""
    try:
        msg = EmailMessage()
        msg["Subject"] = "SAP Automation Report"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content("SAP automation process completed. See attached screenshot.")
        
        with open(screenshot_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="image", subtype="png", filename="report.png")
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        logging.info("Email notification sent successfully")
    except smtplib.SMTPException as e:
        logging.error(f"Email sending failed: {str(e)}")
        raise

def main():
    driver = None
    try:
        driver = initialize_driver()
        logging.info(f"Accessing SAP portal: {SAP_URL}")
        driver.get(SAP_URL)
        
        handle_login(driver)
        
        # Capture screenshot
        time.sleep(5)  # Allow page stabilization
        screenshot_path = "sap_report.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Screenshot saved to {screenshot_path}")
        
        send_email_notification(screenshot_path)
        
    except Exception as e:
        logging.error(f"Automation failed: {str(e)}", exc_info=True)
        if driver:
            driver.save_screenshot("error_screenshot.png")
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Browser session terminated")

if __name__ == "__main__":
    main()
