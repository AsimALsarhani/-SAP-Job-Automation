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

# Environment Configuration
SAP_USERNAME = os.environ.get("SAP_USERNAME")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")  # Replace if needed
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")  # Replace if needed
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")  # Replace if needed
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
    Confirms login by waiting for the 'Save' button (after scrolling it into view) to be clickable.
    """
    # Use a flexible selector that finds any element whose id contains ":_saveBtn"
    SAVE_BUTTON_SELECTOR = (By.XPATH, "//*[contains(@id, ':_saveBtn')]")
    last_exception = None

    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt: {attempt + 1}/{max_retries}")
            logging.info("Navigating to SAP URL...")
            driver.get(SAP_URL)
            time.sleep(2)

            # Optional: Handle frame if needed.
            try:
                WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frameID")))
                logging.info("Switched to frame (if present).")
            except TimeoutException:
                logging.info("No frame found, proceeding without switching.")

            time.sleep(1)

            # Enter username.
            logging.info("Waiting for username field...")
            username_field = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, "username")))
            logging.info("Username field found. Sending keys...")
            username_field.clear()
            username_field.send_keys(SAP_USERNAME)

            # Enter password.
            logging.info("Waiting for password field...")
            password_field = WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, "password")))
            logging.info("Password field found. Sending keys.")
            password_field.clear()
            password_field.send_keys(SAP_PASSWORD)

            # Click Sign In button.
            logging.info("Waiting for Sign In button...")
            try:
                sign_in_button = WebDriverWait(driver, 90).until(EC.element_to_be_clickable((By.ID, "signIn")))
            except TimeoutException:
                logging.info("Sign In button not found by ID, trying alternative locator.")
                sign_in_button = WebDriverWait(driver, 90).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]"))
                )
            logging.info("Sign In button found. Clicking.")
            driver.execute_script("arguments[0].click();", sign_in_button)
            time.sleep(2)

            # --- Verification: Wait for Save button ---
            logging.info("Waiting for Save button presence in DOM...")
            wait = WebDriverWait(driver, 90)
            save_button_element = wait.until(EC.presence_of_element_located(SAVE_BUTTON_SELECTOR))
            logging.info("Save button present in DOM.")

            logging.info("Scrolling Save button into view...")
            driver.execute_script("arguments[0].scrollIntoView(true);", save_button_element)
            time.sleep(0.5)

            logging.info("Waiting for Save button to be clickable after scrolling...")
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable(SAVE_BUTTON_SELECTOR))
            logging.info("Save button is clickable. Assuming login successful.")
            return

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

def main_execution():
    """Main workflow controller."""
    driver = None
    wait_time_short = 60
    wait_time_long = 90

    # Use a flexible selector for the Save button.
    SAVE_BUTTON_SELECTOR = (By.XPATH, "//*[contains(@id, ':_saveBtn')]")
    
    try:
        driver = initialize_browser()
        perform_login(driver)
        logging.info("Login confirmed, performing post-login actions...")
        time.sleep(1)
        
        # --- Step 1: Click Save button again ---
        try:
            logging.info("Re-locating Save button for click action...")
            save_button = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(SAVE_BUTTON_SELECTOR)
            )
            logging.info("Clicking Save button using JavaScript...")
            driver.execute_script("arguments[0].click();", save_button)
            logging.info("Save button clicked.")
            time.sleep(2)
        except (NoSuchElementException, TimeoutException) as e:
            logging.warning(f"Could not click the 'Save' button after login: {e}")
        
        # --- Step 2: Click Careers Site link with retry logic ---
        try:
            logging.info("Waiting for Careers Site link...")
            # Use a flexible, case-insensitive XPath for the Careers Site link.
            careers_link_selector = (By.XPATH, "//a[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'careers site') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'careers site')]")
            for attempt in range(3):
                try:
                    logging.info(f"Attempt {attempt + 1} to locate Careers Site link...")
                    careers_link = WebDriverWait(driver, wait_time_short).until(
                        EC.element_to_be_clickable(careers_link_selector)
                    )
                    logging.info("Scrolling Careers Site link into view...")
                    driver.execute_script("arguments[0].scrollIntoView(true);", careers_link)
                    time.sleep(0.5)
                    logging.info("Clicking Careers Site link using JavaScript...")
                    driver.execute_script("arguments[0].click();", careers_link)
                    logging.info("Careers Site link clicked.")
                    # Immediately log current URL and title
                    current_url = driver.current_url
                    current_title = driver.title
                    logging.info(f"Immediately after click: URL = {current_url}, Title = {current_title}")
                    # Wait until title is exactly "Career Opportunities: My Profile" (adjust if needed)
                    WebDriverWait(driver, wait_time_long).until(
                        lambda drv: "career opportunities: my profile" in drv.title.lower()
                    )
                    logging.info("Navigation to Careers Site confirmed by title.")
                    break
                except (TimeoutException, StaleElementReferenceException) as e:
                    logging.warning(f"Attempt {attempt + 1} to click Careers Site link failed: {e}")
                    if attempt < 2:
                        time.sleep(2)
                    else:
                        logging.error("All attempts to locate and click Careers Site link failed.")
                        raise e
        except Exception as e:
            logging.error(f"Error clicking Careers Site link: {e}")
            raise
        
        # --- Step 3: Click candidate profile area (div) ---
        try:
            logging.info("Waiting for candidate profile div (child of #rcmCandidateProfileCtr)...")
            candidate_div_selector = (By.CSS_SELECTOR, "#rcmCandidateProfileCtr > div:nth-of-type(6)")
            candidate_div = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(candidate_div_selector)
            )
            logging.info("Clicking candidate profile div using ActionChains with offset (195, 64.78)...")
            ActionChains(driver).move_to_element_with_offset(candidate_div, 195, 64.78).click().perform()
            logging.info("Candidate profile div clicked.")
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Error clicking candidate profile div: {e}")
            raise e
        
        # --- Step 4: Right-click on main candidate container ---
        try:
            logging.info("Waiting for candidate container (#rcmCandidateProfileCtr) for right-click...")
            main_candidate = WebDriverWait(driver, wait_time_short).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#rcmCandidateProfileCtr"))
            )
            logging.info("Performing right-click at offset (12, 771.29)...")
            ActionChains(driver).move_to_element_with_offset(main_candidate, 12, 771.29).context_click().perform()
            logging.info("Right-click action performed on candidate container.")
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Error performing right-click on candidate container: {e}")
            raise e
        
        # --- Step 5: Left-click on candidate container at a different offset ---
        try:
            logging.info("Performing left-click on candidate container at offset (0, 813.29)...")
            ActionChains(driver).move_to_element_with_offset(main_candidate, 0, 813.29).click().perform()
            logging.info("Left-click action performed on candidate container.")
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Error performing left-click on candidate container: {e}")
            raise e
        
        # --- Step 6: KeyDown events for 'Control' and 'Shift' ---
        try:
            logging.info("Sending keyDown event for 'Control'...")
            ActionChains(driver).key_down('Control').perform()
            logging.info("Sending keyDown event for 'Shift'...")
            ActionChains(driver).key_down('Shift').perform()
            logging.info("KeyDown events executed.")
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Error sending keyDown events: {e}")
            raise e
        
        logging.info("Post-login actions completed.")
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
