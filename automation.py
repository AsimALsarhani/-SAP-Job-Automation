import os
import logging
import smtplib
import tempfile
import time
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Environment variables configuration
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = "asimalsarhani@gmail.com"
HEADLESS_MODE = os.environ.get("HEADLESS_MODE", "true").lower() == "true"

# Configure logging
log_format = "%(asctime)s - %(levelname)s - %(message)s"
log_handler = RotatingFileHandler(
    "selenium_debug.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)
logging.basicConfig(
    handlers=[log_handler],
    level=logging.INFO,
    format=log_format,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# SMTP configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_TIMEOUT = 10

class SAPPortalError(Exception):
    """Custom exception for SAP portal interactions"""

@contextmanager
def webdriver_context() -> WebDriver:
    """Context manager for WebDriver initialization and cleanup"""
    driver = initialize_webdriver()
    try:
        yield driver
    finally:
        driver.quit()
        logger.info("WebDriver session closed")

def initialize_webdriver() -> WebDriver:
    """Initialize and configure Chrome WebDriver"""
    options = Options()
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    if HEADLESS_MODE:
        options.add_argument("--headless=new")
    
    with tempfile.TemporaryDirectory() as user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception as e:
            logger.error("WebDriver initialization failed: %s", e)
            raise

def send_email(screenshot_path: str) -> None:
    """Send email with screenshot attachment"""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = "SAP Job Portal Automation Report"

    body_text = (
        "Please find attached the automation result "
        "from the SAP job portal."
    )
    msg.attach(MIMEText(body_text, "plain"))

    try:
        with open(screenshot_path, "rb") as img_file:
            img_data = img_file.read()
            img = MIMEImage(img_data, name=os.path.basename(screenshot_path))
            msg.attach(img)
    except IOError as e:
        logger.error("Failed to attach screenshot: %s", e)
        return

    try:
        with smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT,
            timeout=SMTP_TIMEOUT
        ) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            logger.info("Email sent to %s", RECIPIENT_EMAIL)
    except smtplib.SMTPException as e:
        logger.error("SMTP error: %s", e)

def take_screenshot(driver: WebDriver, name: str) -> str:
    """Take screenshot and return file path"""
    filename = f"{name}_{int(time.time())}.png"
    driver.save_screenshot(filename)
    return filename

def safe_click(driver: WebDriver, locator: tuple, timeout: int = 20) -> None:
    """Safely click an element with error handling"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()
    except Exception as e:
        logger.error("Failed to click element %s: %s", locator, e)
        raise SAPPortalError(f"Click failed on {locator}") from e

def sign_in(driver: WebDriver) -> None:
    """Handle SAP portal authentication"""
    login_url = (
        "https://career23.sapsf.com/career?"
        "career_company=saudiara05&lang=en_US"
    )
    try:
        driver.get(login_url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "username"))
        
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)
        
        safe_click(driver, (By.XPATH, "//button[@data-testid='signInButton']"))
        
        WebDriverWait(driver, 30).until(
            lambda d: "login" not in d.current_url.lower()
        )
        take_screenshot(driver, "login_success")

    except Exception as e:
        screenshot = take_screenshot(driver, "login_error")
        send_email(screenshot)
        raise SAPPortalError("Login failed") from e

def execute_portal_actions(driver: WebDriver) -> None:
    """Execute main portal actions"""
    try:
        safe_click(driver, (By.XPATH, "//button[@data-testid='saveButton']"))
        take_screenshot(driver, "save_confirmation")

        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "lastSaveTimeMsg"))
        
        system_messages = driver.find_element(By.ID, "2556:_sysMsgUl")
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth'});",
            system_messages
        )
        take_screenshot(driver, "system_messages")

    except Exception as e:
        screenshot = take_screenshot(driver, "action_error")
        send_email(screenshot)
        raise SAPPortalError("Actions failed") from e

def main() -> None:
    """Main execution flow"""
    try:
        with webdriver_context() as driver:
            sign_in(driver)
            execute_portal_actions(driver)
            success_screenshot = take_screenshot(driver, "final_result")
            send_email(success_screenshot)
    except Exception as e:
        logger.error("Execution failed: %s", e)
        raise

if __name__ == "__main__":
    main()
