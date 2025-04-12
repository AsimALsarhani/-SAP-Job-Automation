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
    StaleElementReferenceException,
    NoSuchFrameException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

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
if not SAP_USERNAME or not SAP_PASSWORD:
    logging.warning("SAP_USERNAME or SAP_PASSWORD environment variable not set.")
if not all("@" in email for email in [SENDER_EMAIL, RECIPIENT_EMAIL]):
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
    """Configure Chrome with optimal headless settings."""
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
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except WebDriverException as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        logging.error("Ensure ChromeDriver is installed and in the system's PATH.")
        raise

def perform_login(driver, max_retries=3, retry_delay=5):
    """
    Execute login with robust error handling and retries.
    Verifies login by waiting for the 'Save' button (scrolling it into view) to be clickable.
    """
    # Use a flexible selector for the Save button (matches any element whose id contains ":_saveBtn")
    SAVE_BUTTON_SELECTOR = (By.XPATH, "//*[contains(@id, ':_saveBtn')]")
    # Use an updated selector for the Sign In button based on ARIA/text.
    SIGN_IN_BUTTON_SELECTOR = (By.XPATH, "//button[@aria-label='Sign In' or normalize-space()='Sign In']")
    
    last_exception = None
    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt: {attempt + 1}/{max_retries}")
            driver.get(SAP_URL)
            time.sleep(2)
            
            # If needed, switch to iframe
            try:
                WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, "frameID"))
                )
                logging.info("Switched to frame (if present).")
            except TimeoutException:
                logging.info("No frame found, proceeding without switching.")
            time.sleep(1)
            
            # Enter username
            logging.info("Waiting for username field...")
            username_field = WebDriverWait(driver, 90).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            logging.info("Username field found. Sending keys...")
            username_field.clear()
            username_field.send_keys(SAP_USERNAME)
            
            # Enter password
            logging.info("Waiting for password field...")
            password_field = WebDriverWait(driver, 90).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            logging.info("Password field found. Sending keys.")
            password_field.clear()
            password_field.send_keys(SAP_PASSWORD)
            
            # Click the Sign In button
            logging.info("Waiting for Sign In button...")
            sign_in_button = WebDriverWait(driver, 90).until(
                EC.element_to_be_clickable(SIGN_IN_BUTTON_SELECTOR)
            )
            logging.info("Sign In button found. Clicking.")
            driver.execute_script("arguments[0].click();", sign_in_button)
            time.sleep(3)  # Wait for login process to proceed
            
            # Scroll down for dynamic content to load
            logging.info("Scrolling to bottom of page...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Verify successful login by waiting for the Save button
            logging.info("Waiting for Save button presence in DOM using selector: " + SAVE_BUTTON_SELECTOR[1])
            wait = WebDriverWait(driver, 120)
            save_button_element = wait.until(EC.presence_of_element_located(SAVE_BUTTON_SELECTOR))
            logging.info("Save button present in DOM.")
            
            logging.info("Scrolling Save button into view...")
            driver.execute_script("arguments[0].scrollIntoView(true);", save_button_element)
            time.sleep(0.5)
            
            logging.info("Waiting for Save button to be clickable after scrolling...")
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable(SAVE_BUTTON_SELECTOR))
            logging.info("Save button is clickable. Login assumed successful.")
            return
        except Exception as e:
            last_exception = e
            logging.error(f"Login attempt {attempt + 1} failed: {e}")
            try:
                logging.error(f"Current URL on failure: {driver.current_url}")
                driver.save_screenshot(f"login_failure_attempt_{attempt + 1}.png")
                logging.info(f"Screenshot saved: login_failure_attempt_{attempt + 1}.png")
            except Exception as se:
                logging.error(f"Error saving screenshot: {se}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying login in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error("Max login retries reached. Raising exception.")
                raise last_exception

def send_report(screenshot_path):
    """Send email report with the final screenshot attached."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logging.error("Sender email or password not configured. Cannot send report.")
        return
    try:
        msg = EmailMessage()
        msg["Subject"] = "SAP Automation Result"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content("Process completed. See attached post-run proof screenshot.")
        with open(screenshot_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="image", subtype="png", filename="post_run_proof.png")
        logging.info(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            logging.info("Logging into email...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            logging.info("Sending email report...")
            server.send_message(msg)
        logging.info("Email dispatched successfully.")
    except Exception as e:
        logging.error(f"Failed to send report: {e}")
        raise

def main_execution():
    """Main workflow controller following the new recorded steps."""
    driver = None
    wait_time_short = 60
    wait_time_long = 120

    # Use a flexible selector for the Save button for login verification.
    SAVE_BUTTON_SELECTOR = (By.XPATH, "//*[contains(@id, ':_saveBtn')]")
    
    try:
        driver = initialize_browser()
        perform_login(driver)
        logging.info("Login confirmed. Proceeding with post-login actions...")
        time.sleep(1)
        
        # Step 1: Click the Save button again
        try:
            logging.info("Re-locating Save button for post-login click...")
            save_button = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(SAVE_BUTTON_SELECTOR)
            )
            logging.info("Clicking Save button using JavaScript...")
            driver.execute_script("arguments[0].click();", save_button)
            logging.info("Save button clicked.")
            time.sleep(3)
        except Exception as e:
            logging.error(f"Failed to click the Save button: {e}")
            driver.save_screenshot("save_button_click_error.png")
            raise
        
        # Step 2: Click inside the main profile container
        try:
            logging.info("Waiting for the main profile container (#rcmCandidateProfileCtr)...")
            profile_container = WebDriverWait(driver, wait_time_short).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#rcmCandidateProfileCtr"))
            )
            logging.info("Profile container found. Scrolling into view...")
            driver.execute_script("arguments[0].scrollIntoView(true);", profile_container)
            time.sleep(0.5)
            logging.info("Clicking the profile container...")
            profile_container.click()
            logging.info("Profile container clicked.")
            time.sleep(2)
        except Exception as e:
            logging.error(f"Failed to click the profile container: {e}")
            driver.save_screenshot("profile_container_click_error.png")
            raise
        
        # Step 7: Zoom out before taking the final screenshot.
        logging.info("Zooming out to capture a wider view...")
        driver.execute_script("document.body.style.zoom='80%'")
        time.sleep(1)  # Allow time for the zoom to take effect
        
        # Step 7: Take final screenshot as post-run proof.
        final_screenshot = "post_run_proof.png"
        driver.save_screenshot(final_screenshot)
        logging.info(f"Final screenshot saved as {final_screenshot}")
        
        send_report(final_screenshot)

    except Exception as e:
        logging.error(f"Critical failure in main execution: {e}", exc_info=True)
        if driver:
            try:
                driver.save_screenshot("critical_error_main.png")
                logging.info("Saved critical_error_main.png")
            except Exception as se:
                logging.error(f"Error saving critical error screenshot: {se}")
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Browser terminated")

if __name__ == "__main__":
    main_execution()
