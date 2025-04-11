import os
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
    NoSuchFrameException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

# Environment Configuration
SAP_USERNAME = os.environ.get("SAP_USERNAME")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza") # Replace with your actual default if needed
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com") # Replace with your actual default if needed
SAP_URL = os.environ.get("SAP_URL")  # Mandatory

# Validation Checks
if not SAP_URL:
    raise ValueError("SAP_URL environment variable must be set")
if not SAP_USERNAME or not SAP_PASSWORD:
     logging.warning("SAP_USERNAME or SAP_PASSWORD environment variable not set.") # Warning instead of fail
# Basic email format check
if not all(["@" in email for email in [SENDER_EMAIL, RECIPIENT_EMAIL]]):
    raise ValueError("Invalid email configuration (SENDER_EMAIL or RECIPIENT_EMAIL)")

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
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36') # Example user agent

    # Set the Chrome binary location (usually handled by PATH in Actions now)
    # chrome_binary_path = os.environ.get("CHROME_PATH", "/usr/bin/google-chrome")
    # options.binary_location = chrome_binary_path

    # Use the ChromeDriver installed at the expected path (usually handled by PATH)
    # chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
    # service = ChromeService(executable_path=chromedriver_path)

    # Simplified setup - relies on driver being in PATH (setup-chrome action does this)
    try:
        driver = webdriver.Chrome(options=options)
        # Remove the webdriver flag for automation evasion
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except WebDriverException as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        logging.error("Ensure ChromeDriver is installed and in the system's PATH.")
        raise


def perform_login(driver, max_retries=5, retry_delay=5):
    """Execute login with robust error handling and retries"""
    # --- !! IMPORTANT !! ---
    # You MUST inspect your SAP portal's HTML after a failed login
    # to find the correct CSS selector for the error message container.
    # Replace '.login-error-class-name' below with the actual selector.
    # Examples: '#error-message', '.sapMessageArea', 'div[data-sap-ui-type="sap.ui.core.HTML"]'
    LOGIN_ERROR_SELECTOR = (By.CSS_SELECTOR, ".login-error-class-name") # <<< --- CHANGE THIS SELECTOR
    LOGIN_SUCCESS_SELECTOR = (By.CSS_SELECTOR, ".sap-main-content")

    last_exception = None # Store last exception for re-raising

    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt: {attempt + 1}/{max_retries}")
            # Navigate on every attempt to ensure clean state
            logging.info("Navigating to SAP URL...")
            driver.get(SAP_URL)
            time.sleep(2) # Small pause for initial load

            # Optional: Frame handling
            try:
                WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frameID")))
                logging.info("Switched to frame (if present).")
            except TimeoutException:
                logging.info("No frame found, proceeding without switching.")

            time.sleep(1)

            # Enter username
            logging.info("Waiting for username field...")
            username_field = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, "username")))
            logging.info("Username field found. Sending keys...")
            username_field.clear()
            username_field.send_keys(SAP_USERNAME)

            # Enter password
            logging.info("Waiting for password field...")
            password_field = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, "password")))
            logging.info("Password field found. Sending keys.")
            password_field.clear()
            password_field.send_keys(SAP_PASSWORD)

            # Click Sign In button
            logging.info("Waiting for Sign In button...")
            try:
                sign_in_button = WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.ID, "signIn")))
            except TimeoutException:
                logging.info("Sign In button not found by ID, trying alternative locator.")
                sign_in_button = WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]")))
            logging.info("Sign In button found. Clicking.")
            # Use JS click as a fallback if normal click fails sometimes
            driver.execute_script("arguments[0].click();", sign_in_button)

            # Wait for EITHER successful login element OR an error message
            logging.info("Waiting for post-login verification OR error message...")
            wait = WebDriverWait(driver, 120) # Increased timeout
            # Use EC.or_ to wait for either condition
            element_found = wait.until(EC.any_of(
                 EC.presence_of_element_located(LOGIN_SUCCESS_SELECTOR),
                 EC.presence_of_element_located(LOGIN_ERROR_SELECTOR)
            ))

            # Check which element was found
            # We need to re-find the element reliably after the wait returns
            try:
                success_element = driver.find_element(*LOGIN_SUCCESS_SELECTOR)
                logging.info("Login successful (found success element).")
                return # Successful login, exit function
            except NoSuchElementException:
                 # Success element not immediately found, check if it was the error element
                 try:
                      error_element = driver.find_element(*LOGIN_ERROR_SELECTOR)
                      error_text = error_element.text.strip()
                      logging.error(f"Login error element found: {error_text}")
                      screenshot_filename = f"login_error_attempt_{attempt + 1}.png"
                      driver.save_screenshot(screenshot_filename)
                      logging.info(f"Screenshot saved: {screenshot_filename}")
                      # Raise a specific error or handle as needed - here we'll raise to stop retries
                      raise Exception(f"Login failed. Error element found: {error_text}")
                 except NoSuchElementException:
                      # Neither success nor error element found after EC.any_of - this shouldn't happen
                      logging.error("EC.any_of succeeded but couldn't find success or error element after.")
                      raise TimeoutException("Post-login state uncertain after wait.")


        except Exception as e: # Catch broader exceptions here
            last_exception = e # Store the exception encountered
            logging.error(f"Login attempt {attempt + 1} failed: {str(e)}")
            screenshot_filename = f"login_failure_attempt_{attempt + 1}.png"
            try:
                logging.error(f"Current URL on failure: {driver.current_url}")
                driver.save_screenshot(screenshot_filename)
                logging.info(f"Screenshot saved: {screenshot_filename}")
                # Log page source snippet
                # logging.error(f"Page source snippet: {driver.page_source[:1000]}")
            except Exception as screenshot_err:
                 logging.error(f"Could not save screenshot or get URL: {screenshot_err}")

            if attempt < max_retries - 1:
                logging.info(f"Retrying login in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # No refresh needed here as we navigate with driver.get() at the start of the loop
            else:
                logging.error("Max login retries reached. Raising last encountered error.")
                raise last_exception # Re-raise the last exception


def send_report(screenshot_path):
    """Send email with attachment"""
    # Basic check for email credentials
    if not SENDER_EMAIL or not SENDER_PASSWORD:
         logging.error("Sender email or password not configured. Cannot send report.")
         return

    try:
        msg = EmailMessage()
        msg["Subject"] = "SAP Automation Result"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content("Process completed. See attached report.")

        with open(screenshot_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="image", subtype="png", filename="report.png")

        logging.info(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            logging.info("Logging into email...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            logging.info("Sending email report...")
            server.send_message(msg)
        logging.info("Email dispatched successfully")

    except smtplib.SMTPAuthenticationError:
         logging.error("SMTP Authentication Error: Check sender email/password and App Password if using Gmail.")
         raise
    except smtplib.SMTPException as e:
        logging.error(f"Email failure (SMTPException): {str(e)}")
        raise
    except Exception as e:
        logging.error(f"General Email failure: {str(e)}")
        raise

def main_execution():
    """Main workflow controller"""
    driver = None
    try:
        driver = initialize_browser()
        # Initial navigation now happens inside perform_login loop
        # logging.info(f"Navigating to SAP portal: {SAP_URL}")
        # driver.get(SAP_URL)

        perform_login(driver) # Call the improved login function

        # Actions after successful login
        logging.info("Login successful, performing post-login actions...")
        time.sleep(3) # Keep pause after login if needed
        screenshot_path = "success_report.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Success screenshot captured: {screenshot_path}")

        send_report(screenshot_path)

    except Exception as e:
        logging.error(f"Critical failure in main execution: {str(e)}", exc_info=True) # Log full traceback
        if driver:
            try:
                driver.save_screenshot("critical_error.png")
                logging.info("Saved critical_error.png")
            except Exception as screen_err:
                 logging.error(f"Could not save critical error screenshot: {screen_err}")
        # Ensure script exits with non-zero status on critical failure
        # The raise statement below achieves this, no need for sys.exit(1)
        raise # Re-raise the exception to mark the workflow as failed
    finally:
        if driver:
            driver.quit()
            logging.info("Browser terminated")

if __name__ == "__main__":
    main_execution()
