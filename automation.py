Here are the two updated code segments:Python Script (automation.py)This is the refined Python script for SAP automation, incorporating best practices for error handling, logging, and browser management.import os
import time
import logging
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Environment Configuration
SAP_USERNAME = os.environ.get("SAP_USERNAME")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD")
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
    handlers=[logging.StreamHandler()],
)


def initialize_browser():
    """Configure Chrome with optimal headless settings"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--disable-features=ChromeWhatsNew")

    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)



def perform_login(driver, max_retries=5, retry_delay=5):
    """Execute login with robust error handling and retries"""
    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt: {attempt + 1}/{max_retries}")

            # Username Entry
            logging.info("Waiting for username field...")
            username_field = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            logging.info("Username field found. Sending keys: %s", SAP_USERNAME)
            username_field.clear()
            username_field.send_keys(SAP_USERNAME)

            # Password Entry
            logging.info("Waiting for password field...")
            password_field = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            logging.info("Password field found. Sending keys.")
            password_field.clear()
            password_field.send_keys(SAP_PASSWORD)

            # Sign In Button
            logging.info("Waiting for Sign In button...")
            # Use a combination of locators for robustness
            sign_in_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.ID, "signIn")
                )
                or EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='submit'][value='Sign In']")  # Added CSS Selector
                )
                or EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(),'Sign In')]") # Added XPath
                )
            )
            logging.info("Sign In button found. Clicking.")
            sign_in_button.click()

            # Post-Login Verification
            logging.info("Waiting for post-login verification element...")
            WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".sap-main-content"))
            )
            logging.info("Login successful")
            return

        except (TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException) as e:
            logging.error(f"Login failure: {str(e)}")
            driver.save_screenshot(f"login_failure_attempt_{attempt + 1}.png")
            logging.error(f"Page source: {driver.page_source}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying login in {retry_delay} seconds...")
                time.sleep(retry_delay)
                driver.refresh()
            else:
                raise
        except WebDriverException as e:
            logging.error(f"WebDriverException: {e}")
            driver.save_screenshot(f"webdriver_exception_{attempt + 1}.png")
            logging.error(f"Page source: {driver.page_source}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying login in {retry_delay} seconds...")
                time.sleep(retry_delay)
                driver.refresh()
            else:
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
        time.sleep(3)
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

