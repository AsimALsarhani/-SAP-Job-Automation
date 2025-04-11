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

# Environment Configuration
SAP_USERNAME = os.environ.get("SAP_USERNAME")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com") # Replace default if needed
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza") # Replace default if needed
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com") # Replace default if needed
SAP_URL = os.environ.get("SAP_URL")  # Mandatory

# Validation Checks
if not SAP_URL:
    raise ValueError("SAP_URL environment variable must be set")
if not SAP_USERNAME or not SAP_PASSWORD:
     logging.warning("SAP_USERNAME or SAP_PASSWORD environment variable not set.")
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
    options.add_argument("--window-size=1920x1080") # Recorder used 866x774, but larger is usually fine
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

def perform_login(driver, max_retries=3, retry_delay=5): # Using max_retries=3
    """Execute login with robust error handling and retries"""
    # --- !! CRITICAL !! ---
    # YOU MUST CHANGE '.login-error-class-name' TO THE *ACTUAL* CSS SELECTOR
    # FOR LOGIN ERROR MESSAGES ON YOUR SAP PORTAL PAGE.
    # Find this using browser Developer Tools (F12) after a failed login.
    LOGIN_ERROR_SELECTOR = (By.CSS_SELECTOR, ".login-error-class-name") # <<< --- CHANGE THIS SELECTOR

    # --- !! CRITICAL !! ---
    # YOU MUST CHANGE '.sap-main-content' TO A *RELIABLE* CSS SELECTOR
    # FOR AN ELEMENT THAT APPEARS *AFTER* SUCCESSFUL LOGIN. Inspect the page shown in the screenshots!
    LOGIN_SUCCESS_SELECTOR = (By.CSS_SELECTOR, ".sap-main-content") # <<< --- CHANGE THIS SELECTOR (Important!)

    last_exception = None

    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt: {attempt + 1}/{max_retries}")
            logging.info("Navigating to SAP URL...")
            driver.get(SAP_URL)
            time.sleep(2)

            try:
                WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frameID")))
                logging.info("Switched to frame (if present).")
            except TimeoutException:
                logging.info("No frame found, proceeding without switching.")

            time.sleep(1)

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

            logging.info("Waiting for Sign In button...")
            try:
                sign_in_button = WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.ID, "signIn")))
            except TimeoutException:
                logging.info("Sign In button not found by ID, trying alternative locator.")
                sign_in_button = WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]")))
            logging.info("Sign In button found. Clicking.")
            driver.execute_script("arguments[0].click();", sign_in_button)

            logging.info("Waiting for post-login verification OR error message...")
            wait = WebDriverWait(driver, 120) # 2 minute wait
            element_found = wait.until(EC.any_of(
                 EC.presence_of_element_located(LOGIN_SUCCESS_SELECTOR), # <<<--- MUST BE CORRECT NOW
                 EC.presence_of_element_located(LOGIN_ERROR_SELECTOR)   # <<<--- Needs correct value
            ))
            logging.info("Found either success or error element after wait.")

            try:
                # Try finding the success element first after the wait returns
                success_element = driver.find_element(*LOGIN_SUCCESS_SELECTOR) # <<<--- MUST BE CORRECT NOW
                logging.info("Login successful (found success element).")
                return # Successful login, exit function
            except NoSuchElementException:
                 logging.info("Success element not found, checking for error element...")
                 try:
                      error_element = driver.find_element(*LOGIN_ERROR_SELECTOR) # <<<--- Needs correct value
                      error_text = error_element.text.strip()
                      logging.error(f"Login error element found with text: '{error_text}'")
                      screenshot_filename = f"login_error_attempt_{attempt + 1}.png"
                      driver.save_screenshot(screenshot_filename)
                      logging.info(f"Screenshot saved: {screenshot_filename}")
                      raise Exception(f"Login failed. Error element found: {error_text}")
                 except NoSuchElementException:
                      logging.error("EC.any_of succeeded but couldn't find success or specified error element immediately after.")
                      screenshot_filename = f"login_ambiguous_state_{attempt + 1}.png"
                      driver.save_screenshot(screenshot_filename)
                      logging.info(f"Screenshot saved: {screenshot_filename}")
                      raise TimeoutException("Post-login state uncertain after wait (neither known success nor known error element found).")

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


def send_report(screenshot_path):
    """Send email with attachment"""
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
    wait_time_short = 30 # Standard wait for elements
    wait_time_long = 90  # Longer wait if needed

    try:
        driver = initialize_browser()

        # --- Step 1: Perform Login (Assumes LOGIN_SUCCESS_SELECTOR is correct!) ---
        perform_login(driver) # Uses default max_retries=3

        # --- Step 2: Actions AFTER successful login ---
        logging.info("Login successful, performing post-login actions based on recording...")
        time.sleep(3) # Allow page to settle after login verification

        # --- Action: Click Save button ---
        # NOTE: Selectors based on recording - MUST BE VERIFIED on actual page!
        # Prefer text or aria-label over potentially dynamic IDs like '#1291:_saveBtn'
        try:
            logging.info("Waiting for Save button...")
            # --- !!! VERIFY/CHANGE THIS SELECTOR based on your page !!! ---
            save_button_selector = (By.XPATH, "//button[normalize-space()='Save' or @aria-label='Save']")
            save_button = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(save_button_selector)
            )
            logging.info("Clicking Save button...")
            save_button.click()
            logging.info("Save button clicked.")
            time.sleep(2) # Pause after action
        except TimeoutException:
            logging.warning("Could not find or click the 'Save' button within timeout.")
            # If Save is mandatory, uncomment the next line:
            # raise Exception("Save button failed - Critical Step")

        # --- Action: Click Careers Site link ---
        # NOTE: Selectors based on recording - MUST BE VERIFIED on actual page!
        # Prefer text or aria-label over fragile positional selectors like 'p:nth-of-type(8) > a'
        try:
            logging.info("Waiting for Careers Site link...")
            # --- !!! VERIFY/CHANGE THIS SELECTOR based on your page !!! ---
            careers_link_selector = (By.XPATH, "//a[normalize-space()='Careers Site' or @aria-label='Careers Site']")
            careers_link = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(careers_link_selector)
            )
            logging.info("Clicking Careers Site link...")
            careers_link.click()
            logging.info("Careers Site link clicked.")
            # IMPORTANT: This likely navigates away. Add waits for the new page if needed.
            logging.info("Waiting for potential navigation after clicking Careers Site (e.g., title change)...")
            # --- !!! VERIFY/ADJUST THIS WAIT CONDITION based on the new page !!! ---
            WebDriverWait(driver, wait_time_long).until(EC.title_contains("Career")) # Example: Waits for title
            time.sleep(3) # Pause after navigation
        except TimeoutException:
            logging.warning("Could not find/click 'Careers Site' link or confirm navigation.")
            # If navigating here is mandatory, uncomment the next line:
            # raise Exception("Navigating to Careers Site failed - Critical Step")

        # --- Action: Other Clicks (Commented Out) ---
        # Purpose unclear from recording, uncomment and verify selectors if needed
        # logging.info("Performing other recorded clicks...")
        # try:
        #     el1 = WebDriverWait(driver, wait_time_short).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#rcmCandidateProfileCtr > div:nth-of-type(6)")))
        #     el1.click()
        #     time.sleep(1)
        #     el2 = WebDriverWait(driver, wait_time_short).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#rcmCandidateProfileCtr")))
        #     el2.click()
        #     time.sleep(1)
        # except TimeoutException:
        #      logging.warning("Could not perform other recorded clicks.")

        # --- Step 3: Final Actions ---
        logging.info("Post-login actions completed.")
        screenshot_path = "final_state_report.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Final state screenshot captured: {screenshot_path}")

        send_report(screenshot_path) # Send email if successful

    except Exception as e:
        logging.error(f"Critical failure in main execution: {str(e)}", exc_info=True)
        if driver:
            try:
                driver.save_screenshot("critical_error_main.png")
                logging.info("Saved critical_error_main.png")
            except Exception as screen_err:
                 logging.error(f"Could not save critical error screenshot: {screen_err}")
        raise # Re-raise exception to ensure workflow fails
    finally:
        if driver:
            driver.quit()
            logging.info("Browser terminated")

if __name__ == "__main__":
    main_execution()
