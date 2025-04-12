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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys # Import Keys

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

# perform_login() function (Updated with page scroll)
def perform_login(driver, max_retries=3, retry_delay=5):
    """Execute login with robust error handling and retries.
       Scrolls page down, then waits for 'Save' button as confirmation."""

    # --- Using the Absolute XPath selector you provided ---
    # !! WARNING: This selector is very fragile and likely to break !!
    SAVE_BUTTON_SELECTOR = (By.XPATH, '/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[1]/div[23]/div/span') # <<< --- Using your XPath
    # --- ---

    last_exception = None

    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt: {attempt + 1}/{max_retries}")
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

            # Enter username/password
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

            # Click Sign In button
            logging.info("Waiting for Sign In button...")
            try:
                sign_in_button = WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.ID, "signIn")))
            except TimeoutException:
                logging.info("Sign In button not found by ID, trying alternative locator.")
                sign_in_button = WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]")))
            logging.info("Sign In button found. Clicking.")
            driver.execute_script("arguments[0].click();", sign_in_button)
            time.sleep(3) # Increase pause slightly after login click

            # --- Scroll Page Down Before Checking for Button ---
            logging.info("Attempting to scroll to page bottom...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1) # Allow time for any lazy loading triggered by scroll
            logging.info("Scrolled to bottom. Now proceeding with Save button check...")
            # --- End Scroll Page Down ---

            # --- VERIFICATION STEPS (After Page Scroll) ---
            # 1. Wait for the Save button to be PRESENT in the DOM
            logging.info(f"Waiting for Save element presence in DOM using: {SAVE_BUTTON_SELECTOR[1]}")
            wait = WebDriverWait(driver, 90) # Still wait up to 90s for presence
            save_button_element = wait.until(
                EC.presence_of_element_located(SAVE_BUTTON_SELECTOR) # <<< --- USES YOUR XPATH
            )
            logging.info("Save element present in DOM.")

            # 2. Scroll the specific element into view (might be redundant now, but safe)
            logging.info("Scrolling Save element specifically into view...")
            driver.execute_script("arguments[0].scrollIntoView(true);", save_button_element)
            time.sleep(0.5)

            # 3. Now wait for the button to be CLICKABLE
            logging.info("Waiting for Save element to be clickable after scroll...")
            WebDriverWait(driver, 30).until( # Shorter wait now it should be visible
                EC.element_to_be_clickable(SAVE_BUTTON_SELECTOR) # <<< --- USES YOUR XPATH
            )
            logging.info("Save element clickable. Assuming login successful.")
            # --- END VERIFICATION STEPS ---

            return # Login presumed successful, exit function

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
    """Send email with attachment."""
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

# main_execution() function (Using your absolute XPath for Save button)
def main_execution():
    """Main workflow controller."""
    driver = None
    wait_time_short = 60
    wait_time_long = 120

    # --- Using the Absolute XPath selector you provided ---
    # !! WARNING: This selector is very fragile !!
    SAVE_BUTTON_SELECTOR = (By.XPATH, '/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[1]/div[23]/div/span') # <<< --- UPDATED WITH YOUR XPATH
    # --- ---

    # --- Selector for Careers Link (Verify this is correct for your page!) ---
    CAREERS_LINK_SELECTOR = (By.XPATH, "//a[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'careers site') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'careers site')]") # <<<--- MUST VERIFY AND CHANGE IF INCORRECT !!!
    # --- ---

    CANDIDATE_DIV_SELECTOR = (By.CSS_SELECTOR, "#rcmCandidateProfileCtr > div:nth-of-type(6)") # Verify if needed
    MAIN_CANDIDATE_SELECTOR = (By.CSS_SELECTOR, "#rcmCandidateProfileCtr") # Verify if needed

    try:
        driver = initialize_browser()
        perform_login(driver) # Uses the updated SAVE_BUTTON_SELECTOR internally
        logging.info("Login confirmed, performing post-login actions...")
        time.sleep(1)

        # --- Action: Click Save button/element ---
        try:
            logging.info("Finding Save element again to click...")
            # We wait for clickable again here just to be sure before clicking
            save_button = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(SAVE_BUTTON_SELECTOR) # <<< --- USES YOUR UPDATED XPATH
            )
            logging.info("Clicking Save element using JavaScript...")
            driver.execute_script("arguments[0].click();", save_button)
            logging.info("Save element clicked.")
            time.sleep(2)
        except Exception as e:
            logging.error(f"Could not click the 'Save' element after login confirmation: {e}", exc_info=True)
            driver.save_screenshot("save_button_click_error.png")
            raise

        # --- Action: Click Careers Site link ---
        # (This part still needs verification of its selector)
        try:
            logging.info("Waiting for Careers Site link...")
            logging.info(f"Waiting for link with selector: {CAREERS_LINK_SELECTOR[1]}")
            careers_link = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(CAREERS_LINK_SELECTOR) # <<< --- VERIFY THIS SELECTOR
            )
            logging.info("Careers link located.")
            logging.info("Scrolling Careers Site link into view...")
            driver.execute_script("arguments[0].scrollIntoView(true);", careers_link)
            time.sleep(0.5)
            logging.info("Attempting to click Careers Site link using JavaScript...")
            driver.execute_script("arguments[0].click();", careers_link)
            logging.info("JS click executed for Careers Site link.")
            time.sleep(1)
            current_url = driver.current_url
            current_title = driver.title
            logging.info(f"Immediately after click: URL = {current_url}, Title = {current_title}")
            logging.info("Waiting for navigation confirmation (title contains 'Career')...")
            WebDriverWait(driver, wait_time_long).until(
                lambda drv: "career" in drv.title.lower()
            )
            logging.info("Navigation to Careers Site confirmed by title.")
        except Exception as e:
            logging.warning(f"Could not find/click 'Careers Site' link or confirm navigation: {e}", exc_info=True)
            driver.save_screenshot("careers_site_click_error.png")
            # Decide if this is critical, raise e?

        # --- Other recorded actions (Commented out, verify if needed) ---
        # ... (ActionChains code remains commented) ...

        # --- Step 3: Final Actions ---
        logging.info("Post-login actions seemingly completed.")
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
