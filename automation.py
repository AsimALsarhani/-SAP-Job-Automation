#!/usr/bin/env python3
import os
import time
import logging
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from urllib.parse import urlparse
import subprocess
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException,
    NoSuchFrameException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Environment Configuration
SAP_USERNAME = os.environ.get("SAP_USERNAME", "asim.s.alsarhani@gmail.com")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "AbuSY@1990")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")
SAP_URL = os.environ.get("SAP_URL", "https://career23.sapsf.com/portalcareer?company=saudiara05&rcm%5fsite%5flocale=en%5fUS&&navBarLevel=MY_PROFILE&_s.crb=G6m7RtwTu3ML9073ujGOG%252bYc58m6hAuHTwz4fy1aNnw%253d")
EMAIL_REPORT = os.environ.get("EMAIL_REPORT", "True").lower() == "true"
HEADLESS_MODE = os.environ.get("HEADLESS_MODE", "True").lower() == "true"

if not SAP_URL:
    raise ValueError("SAP_URL environment variable must be set.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

def send_email_report(subject, body, sender_email, sender_password, recipient_email, screenshot_path=None):
    if not EMAIL_REPORT:
        logging.info("Email reporting is disabled.")
        return

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if screenshot_path:
        try:
            with open(screenshot_path, "rb") as img_file:
                img = MIMEImage(img_file.read(), name=os.path.basename(screenshot_path))
                msg.attach(img)
        except Exception as e:
            logging.error(f"Error attaching screenshot: {e}")

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        logging.info("Email report sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise

def initialize_browser():
    """
    Initializes the Chrome WebDriver with specified options,
    including a unique user data directory and explicitly sets the chrome binary location.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--log-level=3")
    if HEADLESS_MODE:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

    # Create a unique user data directory
    unique_dir = f"/tmp/chrome_userdata_{uuid.uuid4()}"
    os.makedirs(unique_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={unique_dir}")
    logging.info(f"Using unique Chrome user data directory: {unique_dir}")

    # Specify the path to the Chrome binary
    chrome_binary_path = "/usr/bin/google-chrome"
    if os.path.exists(chrome_binary_path):
        options.binary_location = chrome_binary_path
        logging.info(f"Chrome binary found at: {chrome_binary_path}")
    else:
        logging.warning(f"Chrome binary not found at: {chrome_binary_path}. Ensure Chrome is installed and the path is correct.")

    # Always use the ChromeDriver at the specified path
    chrome_service = ChromeService(executable_path="/usr/bin/chromedriver")
    try:
        driver = webdriver.Chrome(service=chrome_service, options=options)
    except WebDriverException as e:
        logging.error(f"WebDriverException during initialization: {e}")
        raise
    return driver, unique_dir

def kill_chrome_processes():
    try:
        subprocess.run(["pkill", "-f", "chrome"], check=False, capture_output=True)
        subprocess.run(["pkill", "-f", "chromium"], check=False, capture_output=True)
        logging.info("Killed any existing Chrome/Chromium processes.")
    except Exception as e:
        logging.error(f"Error killing Chrome processes: {e}")

def remove_lock_files(user_data_dir):
    lock_files = ["lockfile", "SingletonLock", "SingletonSocket", "SingletonCookie"]
    if not os.path.exists(user_data_dir):
        logging.warning(f"User data directory does not exist: {user_data_dir}")
        return
    for filename in lock_files:
        lock_file_path = os.path.join(user_data_dir, filename)
        if os.path.exists(lock_file_path):
            try:
                os.remove(lock_file_path)
                logging.info(f"Removed lock file: {lock_file_path}")
            except Exception as e:
                logging.error(f"Error removing lock file {lock_file_path}: {e}")

def check_permissions(user_data_dir):
    if not os.path.exists(user_data_dir):
        logging.warning(f"User data directory does not exist: {user_data_dir}")
        return
    try:
        st = os.stat(user_data_dir)
        uid = st.st_uid
        gid = st.st_gid
        mode = oct(st.st_mode & 0o777)
        logging.info(f"User data directory permissions: Owner={uid}, Group={gid}, Mode={mode}, Path={user_data_dir}")
        if os.access(user_data_dir, os.W_OK):
            logging.info(f"User data directory is writable: {user_data_dir}")
        else:
            logging.error(f"User data directory is not writable: {user_data_dir}")
    except Exception as e:
        logging.error(f"Error checking permissions of {user_data_dir}: {e}")

def perform_login(driver, max_retries=3, retry_delay=5):
    def locate_and_fill_element(by, value, keys):
        try:
            element = WebDriverWait(driver, 120).until(EC.presence_of_element_located((by, value)))
            element.clear()
            element.send_keys(keys)
            return element
        except Exception as e:
            raise WebDriverException(f"Failed to locate or interact with element {by}={value}: {e}")

    parsed_url = urlparse(SAP_URL)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt: {attempt + 1}/{max_retries}")
            driver.get(SAP_URL)
            try:
                WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frameID")))
                logging.info("Switched to frame (if present).")
            except TimeoutException:
                logging.info("No frame found, proceeding without switching.")

            WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(1)

            locate_and_fill_element(By.ID, "username", SAP_USERNAME)
            locate_and_fill_element(By.ID, "password", SAP_PASSWORD)

            try:
                sign_in_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "signIn")))
                logging.info("Sign In button found by ID.")
            except TimeoutException:
                sign_in_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]")))
                logging.info("Sign In button found by XPath.")

            if sign_in_button:
                logging.info("Clicking the Sign In button.")
                driver.execute_script("arguments[0].click();", sign_in_button)
            else:
                raise NoSuchElementException("Sign In button not located.")

            WebDriverWait(driver, 120).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sap-main-content")),
                    EC.presence_of_element_located((By.ID, "error-message")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".error")),
                    EC.title_contains("Error"),
                    EC.url_changes(base_url)
                )
            )

            page_source_lower = driver.page_source.lower()
            if "error" in page_source_lower or "failed" in page_source_lower:
                error_message = "Login failed due to error message on page."
                logging.error(error_message)
                driver.save_screenshot("login_error_page.png")
                send_email_report(
                    "SAP Automation - Login Failed",
                    "Login failed due to an error message on the page.",
                    SENDER_EMAIL,
                    SENDER_PASSWORD,
                    RECIPIENT_EMAIL,
                )
                raise WebDriverException(error_message)

            if "Sign In" in driver.title:
                error_message = "Login failed: Still on the Sign In page."
                logging.error(error_message)
                driver.save_screenshot("login_error_signin_page.png")
                send_email_report(
                    "SAP Automation - Login Failed",
                    "Login failed: Still on the Sign In page after login attempt.",
                    SENDER_EMAIL,
                    SENDER_PASSWORD,
                    RECIPIENT_EMAIL,
                )
                raise WebDriverException(error_message)

            logging.info("Login successful.")
            return

        except Exception as e:
            logging.error(f"Login failure: {str(e)}")
            screenshot_name = f"login_failure_attempt_{attempt + 1}.png"
            driver.save_screenshot(screenshot_name)
            logging.error(f"Screenshot saved as {screenshot_name}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying login in {retry_delay} seconds...")
                time.sleep(retry_delay)
                driver.refresh()
            else:
                send_email_report(
                    "SAP Automation - Login Failed",
                    f"Login failed after {max_retries} attempts. Error: {str(e)}",
                    SENDER_EMAIL,
                    SENDER_PASSWORD,
                    RECIPIENT_EMAIL,
                )
                raise

def get_chrome_version():
    try:
        result = subprocess.run(["google-chrome", "--version"], capture_output=True, text=True, check=True)
        version_string = result.stdout.strip()
        version_number = result.stdout.split("Chrome ")[1].split(".")[0]
        return version_number
    except Exception as e:
        logging.error(f"Error getting Chrome version: {e}")
        return None

def main():
    driver = None
    driver_user_data_dir = None
    try:
        kill_chrome_processes()

        chrome_version = get_chrome_version()
        if chrome_version:
            logging.info(f"Detected Chrome version: {chrome_version}")
        else:
            logging.warning("Could not detect Chrome version. Using default driver behavior.")

        driver, driver_user_data_dir = initialize_browser()
        perform_login(driver)

        logging.info("Proceeding with post-login automation tasks...")

        # Example post-login automation steps
        save_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ACCESSIBILITY_LABEL, "Save"))
        )
        save_button.click()
        logging.info("Clicked 'Save' button.")

        careers_site_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ACCESSIBILITY_LABEL, "Careers Site"))
        )
        careers_site_link.click()
        logging.info("Clicked 'Careers Site' link.")

        profile_section = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#rcmCandidateProfileCtr"))
        )
        profile_section.click()
        logging.info("Clicked on #rcmCandidateProfileCtr")

        time.sleep(50)
        logging.info("Waited for 50 seconds.")

        driver.refresh()
        logging.info("Reloaded the page.")

        driver.execute_script("window.scrollTo(0, 0);")
        logging.info("Scrolled to the top of the page.")

        try:
            update_notification = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".latest-update-notification"))
            )
            logging.info("Found latest update notification.")
            update_notification.click()
            logging.info("Clicked on the latest update notification")
        except TimeoutException:
            logging.warning("Could not find the latest update notification.")

        screenshot_path = "update_notification.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Saved screenshot: {screenshot_path}")

        send_email_report(
            "SAP Automation - Success",
            "SAP automation script completed successfully. Screenshot of update notification attached.",
            SENDER_EMAIL,
            SENDER_PASSWORD,
            RECIPIENT_EMAIL,
            screenshot_path
        )

    except Exception as ex:
        logging.error(f"Automation job failed: {ex}")
        send_email_report(
            "SAP Automation - Job Failed",
            f"SAP automation script failed. Error: {str(ex)}",
            SENDER_EMAIL,
            SENDER_PASSWORD,
            RECIPIENT_EMAIL,
        )
    finally:
        if driver:
            driver.quit()
        logging.info("Driver closed. Automation job completed.")
        if driver_user_data_dir and os.path.exists(driver_user_data_dir):
            shutil.rmtree(driver_user_data_dir)
            logging.info(f"Deleted driver user data directory: {driver_user_data_dir}")

if __name__ == "__main__":
    main()
