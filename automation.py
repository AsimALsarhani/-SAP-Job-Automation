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
from selenium.webdriver.common.action_chains import ActionChains # Import ActionChains


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

# perform_login() function (Keep as is - seems to be working now)
def perform_login(driver, max_retries=3, retry_delay=5):
    """
    Execute login with robust error handling and retries.
    Waits for the 'Save' button (after scrolling it into view) to be clickable.
    """
    SAVE_BUTTON_SELECTOR = (By.XPATH, "//*[contains(@id, ':_saveBtn')]") # Flexible selector
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
                sign_in_button = WebDriverWait(driver, 90).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]"))
                )
            logging.info("Sign In button found. Clicking.")
            driver.execute_script("arguments[0].click();", sign_in_button)
            time.sleep(2)
            logging.info("Waiting for 'Save' button presence in DOM...")
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

# ---vvv--- Modified main_execution() with more debugging ---vvv---
def main_execution():
    """Main workflow controller."""
    driver = None
    wait_time_short = 60 # Increased from 30
    wait_time_long = 120 # Increased from 90

    SAVE_BUTTON_SELECTOR = (By.XPATH, "//*[contains(@id, ':_saveBtn')]")
    CAREERS_LINK_SELECTOR = (By.XPATH, "//a[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'careers site') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'careers site')]")
    CANDIDATE_DIV_SELECTOR = (By.CSS_SELECTOR, "#rcmCandidateProfileCtr > div:nth-of-type(6)")
    MAIN_CANDIDATE_SELECTOR = (By.CSS_SELECTOR, "#rcmCandidateProfileCtr")

    try:
        driver = initialize_browser()
        perform_login(driver)
        logging.info("Login confirmed, performing post-login actions...")
        time.sleep(1)

        # --- Action: Click Save button ---
        try:
            logging.info("Finding Save button again to click...")
            save_button = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(SAVE_BUTTON_SELECTOR)
            )
            logging.info("Clicking Save button using JavaScript...")
            driver.execute_script("arguments[0].click();", save_button)
            logging.info("Save button clicked.")
            time.sleep(2)
        except Exception as e: # Catch broader exception
            logging.error(f"Could not click the 'Save' button after login confirmation: {e}", exc_info=True)
            # Save screenshot specific to this failure
            driver.save_screenshot("save_button_click_error.png")
            raise # Re-raise to stop execution if Save is critical

        # --- Action: Click Careers Site link with retry logic and more debug ---
        careers_clicked = False
        for attempt in range(3):
            try:
                logging.info(f"Attempt {attempt + 1}/3 to find and click Careers Site link...")
                logging.info(f"Waiting for link with selector: {CAREERS_LINK_SELECTOR[1]}")
                # Save screenshot BEFORE trying to find/click
                pre_careers_click_screenshot = f"careers_site_before_click_attempt_{attempt + 1}.png"
                driver.save_screenshot(pre_careers_click_screenshot)
                logging.info(f"Saved screenshot: {pre_careers_click_screenshot}")

                careers_link = WebDriverWait(driver, wait_time_short).until(
                    EC.element_to_be_clickable(CAREERS_LINK_SELECTOR)
                )
                logging.info("Careers link located.")
                logging.info("Scrolling Careers Site link into view...")
                driver.execute_script("arguments[0].scrollIntoView(true);", careers_link)
                time.sleep(0.5) # Pause after scroll

                logging.info("Attempting to click Careers Site link using JavaScript...")
                driver.execute_script("arguments[0].click();", careers_link)
                logging.info("JS click executed for Careers Site link.")
                time.sleep(1) # Pause to allow navigation/JS action to start

                # Immediately log current URL and title after click attempt
                current_url = driver.current_url
                current_title = driver.title
                logging.info(f"Immediately after click: URL = {current_url}, Title = {current_title}")

                logging.info("Waiting for navigation confirmation (title contains 'Career')...")
                WebDriverWait(driver, wait_time_long).until(
                    lambda drv: "career" in drv.title.lower() # Broader check, case-insensitive
                )
                logging.info("Navigation to Careers Site confirmed by title.")
                careers_clicked = True
                break # Exit loop if successful
            except (TimeoutException, StaleElementReferenceException, WebDriverException) as e:
                logging.warning(f"Attempt {attempt + 1}/3 to click Careers Site link failed: {e}")
                post_careers_click_screenshot = f"careers_site_click_error_attempt_{attempt + 1}.png"
                try:
                    driver.save_screenshot(post_careers_click_screenshot)
                    logging.info(f"Saved error screenshot: {post_careers_click_screenshot}")
                except Exception as screen_err:
                    logging.error(f"Could not save screenshot on careers click error: {screen_err}")
                if attempt < 2:
                    logging.info("Waiting before retry...")
                    time.sleep(5) # Wait longer before retry
                else:
                    logging.error("All attempts to locate and click Careers Site link failed.")
                    raise # Re-raise the last exception if all retries fail
        # Check if click was successful before proceeding
        if not careers_clicked:
             raise Exception("Critical step failed: Could not click Careers Site link.")


        # --- Action: Click candidate profile area (div) ---
        try:
            logging.info("Waiting for candidate profile div...")
            candidate_div = WebDriverWait(driver, wait_time_short).until(
                EC.element_to_be_clickable(CANDIDATE_DIV_SELECTOR)
            )
            logging.info("Clicking candidate profile div using ActionChains with offset...")
            ActionChains(driver).move_to_element_with_offset(candidate_div, 195, 64.78).click().perform()
            logging.info("Candidate profile div clicked.")
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Error clicking candidate profile div: {e}", exc_info=True)
            driver.save_screenshot("profile_div_click_error.png")
            raise # Optional: decide if this is critical

        # --- Action: Right-click on main candidate container ---
        try:
            logging.info("Waiting for candidate container for right-click...")
            main_candidate = WebDriverWait(driver, wait_time_short).until(
                EC.presence_of_element_located(MAIN_CANDIDATE_SELECTOR)
            )
            logging.info("Performing right-click at offset...")
            ActionChains(driver).move_to_element_with_offset(main_candidate, 12, 771.29).context_click().perform()
            logging.info("Right-click action performed.")
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Error performing right-click on candidate container: {e}", exc_info=True)
            driver.save_screenshot("profile_rclick_error.png")
            raise # Optional: decide if this is critical

        # --- Action: Left-click on candidate container at a different offset ---
        try:
            # Re-find element in case DOM changed
            main_candidate = WebDriverWait(driver, wait_time_short).until(
                EC.presence_of_element_located(MAIN_CANDIDATE_SELECTOR)
            )
            logging.info("Performing left-click on candidate container at offset...")
            ActionChains(driver).move_to_element_with_offset(main_candidate, 0, 813.29).click().perform()
            logging.info("Left-click action performed.")
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Error performing left-click on candidate container: {e}", exc_info=True)
            driver.save_screenshot("profile_lclick_error.png")
            raise # Optional: decide if this is critical

        # --- Action: KeyDown events for 'Control' and 'Shift' ---
        # These are less likely to cause critical failures but wrapping anyway
        try:
            logging.info("Sending keyDown event for 'Control'...")
            ActionChains(driver).key_down(Keys.CONTROL).perform() # Use Keys enum if available
            logging.info("Sending keyDown event for 'Shift'...")
            ActionChains(driver).key_down(Keys.SHIFT).perform() # Use Keys enum
            logging.info("KeyDown events executed.")
            # IMPORTANT: Remember to release keys if needed!
            # ActionChains(driver).key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Error sending keyDown events: {e}", exc_info=True)
            # Optional: Decide if this should raise

        # --- Step 3: Final Actions ---
        logging.info("Post-login actions seemingly completed.")
        screenshot_path = "final_state_report.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Final state screenshot captured: {screenshot_path}")

        send_report(screenshot_path)

    except Exception as e:
        logging.error(f"Critical failure in main execution: {str(e)}", exc_info=True) # Log full traceback
        if driver:
            try:
                # Save screenshot with a name indicating critical failure
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
    # Import Keys if needed for ActionChains key_down/key_up
    from selenium.webdriver.common.keys import Keys
    main_execution()
