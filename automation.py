# automation.py
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
from selenium.webdriver.common.action_chains import ActionChains # Still needed for potential future use
from selenium.webdriver.common.keys import Keys

# Environment Configuration (Keep as is)
SAP_USERNAME = os.environ.get("SAP_USERNAME")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")
SAP_URL = os.environ.get("SAP_URL")

# Validation Checks (Keep as is)
if not SAP_URL:
    raise ValueError("SAP_URL environment variable must be set")
if not SAP_USERNAME or not SAP_PASSWORD:
    logging.warning("SAP_USERNAME or SAP_PASSWORD environment variable not set.")
if not all(["@" in email for email in [SENDER_EMAIL, RECIPIENT_EMAIL]]):
    raise ValueError("Invalid email configuration (SENDER_EMAIL or RECIPIENT_EMAIL)")

# Email Settings (Keep as is)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Logging Configuration (Keep as is)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

# initialize_browser() function (Keep as is)
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

# perform_login() function (Updated Sign In and Save selectors based on new recording)
def perform_login(driver, max_retries=3, retry_delay=5):
    """Execute login with robust error handling and retries.
       Scrolls page down, then waits for 'Save' button as confirmation."""

    # --- Selectors based on new recording ---
    # Prioritize ARIA/Text, fall back to others if needed. VERIFY THESE!
    SIGN_IN_BUTTON_SELECTOR = (By.XPATH, "//button[@aria-label='Sign In' or normalize-space()='Sign In']") # Check aria-label or text first
    # Fallback if above fails (less reliable):
    # SIGN_IN_BUTTON_SELECTOR = (By.CSS_SELECTOR, "#outershell button")

    # Using ARIA/Text for Save button is preferred over the fragile ID from recording
    SAVE_BUTTON_SELECTOR = (By.XPATH, "//button[@aria-label='Save' or normalize-space()='Save']") # <<<--- CHECK IF THIS WORKS
    # Fallback to fragile ID from recording if necessary:
    # SAVE_BUTTON_SELECTOR = (By.XPATH, '//*[@id="1291:_saveBtn"]')
    # --- ---

    last_exception = None

    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt: {attempt + 1}/{max_retries}")
            if attempt > 0:
                logging.info("Clearing cookies before retry...")
                driver.delete_all_cookies()
                time.sleep(1)
            logging.info("Navigating to SAP URL...")
            driver.get(SAP_URL)
            time.sleep(2)

            # Optional: Frame handling
            try:
                WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frameID")))
                logging.info("Switched to frame (if present).")
            except TimeoutException:
                logging.info("No frame found, proceeding without switching.")
            time.sleep(1)

            # Enter username/password (Selectors seem stable)
            logging.info("Waiting for username field...")
            username_field = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, "username")))
            logging.info("Username field found. Sending keys...")
            username_field.clear()
            username_field.send_keys(SAP_USERNAME)

            logging.info("Waiting for password field...")
            password_field = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, "password")))
            logging.info("Password field found. Sending keys.")
            password_field.clear()
            password_field.send_keys(SAP_PASSWORD)

            # Click Sign In button (Using updated selector)
            logging.info("Waiting for Sign In button...")
            sign_in_button = WebDriverWait(driver, 90).until(
                EC.element_to_be_clickable(SIGN_IN_BUTTON_SELECTOR) # Use new selector
            )
            logging.info("Sign In button found. Clicking.")
            driver.execute_script("arguments[0].click();", sign_in_button)
            time.sleep(3) # Increase pause after login click

            # --- Scroll Page Down Before Checking for Save Button ---
            logging.info("Attempting to scroll to page bottom...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            logging.info("Scrolled to bottom. Now checking for Save button...")
            # --- End Scroll Page Down ---

            # --- VERIFICATION STEPS (Using updated Save selector) ---
            logging.info(f"Waiting for Save button presence in DOM using: {SAVE_BUTTON_SELECTOR[1]}")
            wait = WebDriverWait(driver, 90)
            save_button_element = wait.until(
                EC.presence_of_element_located(SAVE_BUTTON_SELECTOR) # Use updated selector
            )
            logging.info("Save button present in DOM.")

            logging.info("Scrolling Save button into view...")
            driver.execute_script("arguments[0].scrollIntoView(true);", save_button_element)
            time.sleep(0.5)

            logging.info("Waiting for Save button to be clickable after scroll...")
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(SAVE_BUTTON_SELECTOR) # Use updated selector
            )
            logging.info("Save button clickable. Assuming login successful.")
            # --- END VERIFICATION STEPS ---

            return # Login successful

        except Exception as e:
            last_exception = e
            logging.error(f"Login attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            screenshot_filename = f"login_failure_attempt_{attempt + 1}.png"
            try:
                logging.error(f"Current URL on failure: {driver.current_url}")
                driver.save_screenshot(screenshot_filename)
                logging.info(f"Screenshot saved: {screenshot_filename}")
            except Exception as screenshot_err:
                 logging.error(f"Could not save screenshot or get URL: {screenshot_err}")

            if attempt < max_retries - 1:
                logging.info(f"Retrying login in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error("Max login retries reached. Raising last encountered error.")
                raise last_exception

# send_report() function (Keep as is)
def send_report(screenshot_path):
    # ... (code remains the same) ...
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


# main_execution() function (Simplified based on new recording)
def main_execution():
    """Main workflow controller."""
    driver = None
    wait_time_short = 60
    wait_time_long = 120 # Keep longer wait for potential page loads

    # --- Selectors based on new recording ---
    # Using ARIA/Text for Save button is preferred over the fragile ID from recording
    SAVE_BUTTON_SELECTOR = (By.XPATH, "//button[@aria-label='Save' or normalize-space()='Save']") # <<<--- CHECK IF THIS WORKS
    # Fallback to fragile ID from recording if necessary:
    # SAVE_BUTTON_SELECTOR = (By.XPATH, '//*[@id="1291:_saveBtn"]')

    # Selector for the profile container click
    PROFILE_CONTAINER_SELECTOR = (By.CSS_SELECTOR, "#rcmCandidateProfileCtr") # Verify if needed
    # --- ---

    try:
        driver = initialize_browser()
        perform_login(driver) # Verifies login by finding Save button
        logging.info("Login confirmed, performing post-login actions from new recording...")
        time.sleep(1)

        # --- Action: Click Save button ---
        # (Already verified as clickable in perform_login)
        try:
            logging.info("Finding Save button again to click...")
            save_button = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(SAVE_BUTTON_SELECTOR)
            )
            logging.info("Clicking Save button using JavaScript...")
            driver.execute_script("arguments[0].click();", save_button)
            logging.info("Save button clicked.")
            time.sleep(3) # Increase pause after save potentially
        except Exception as e:
            logging.error(f"Could not click the 'Save' button after login confirmation: {e}", exc_info=True)
            driver.save_screenshot("save_button_click_error.png")
            raise

        # --- Action: Click within Profile Container ---
        # Recording showed a click here, purpose unclear, but replicating it.
        try:
            logging.info("Waiting for profile container...")
            profile_container = WebDriverWait(driver, wait_time_short).until(
                EC.presence_of_element_located(PROFILE_CONTAINER_SELECTOR)
            )
            # Recording used offset, but maybe just clicking container is enough?
            # Or find a specific sub-element if needed.
            logging.info("Clicking profile container...")
            profile_container.click()
            # ActionChains(driver).move_to_element_with_offset(profile_container, 596, 670.28).click().perform() # If specific offset needed
            logging.info("Clicked profile container.")
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Could not click profile container: {e}", exc_info=True)
            driver.save_screenshot("profile_container_click_error.png")
            # Decide if this is critical, raise e?


        # --- Removed Careers Site click and other previous steps ---

        # --- Final Actions ---
        logging.info("Post-login actions from new recording completed.")
        screenshot_path = "final_state_report.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Final state screenshot captured: {screenshot_path}")

        send_report(screenshot_path)

    except Exception as e:
        logging.error(f"Critical failure in main execution: {str(e)}", exc_info=True)
        if driver:
            try:
                driver.save_screenshot("critical_error_main.png")
                logging.info("Saved critical_error_main.png")
            except Exception as screen_err:
                 logging.error(f"Could not save critical error screenshot: {screen_err}")
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Browser terminated")

if __name__ == "__main__":
    main_execution()
