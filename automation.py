#!/usr/bin/env python3
import os
import time
import logging
import tempfile

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
    NoSuchFrameException
)
from webdriver_manager.chrome import ChromeDriverManager

# Environment Configuration
SAP_USERNAME = os.environ.get("SAP_USERNAME", "asim.s.alsarhani@gmail.com")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "AbuSY@1990")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")
SAP_URL = os.environ.get("SAP_URL")  # Mandatory

if not SAP_URL:
    raise ValueError("SAP_URL environment variable must be set.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler()
    ]
)

def perform_login(driver, max_retries=3, retry_delay=5):
    """Execute login with robust error handling, retries, and enhanced logging."""
    for attempt in range(max_retries):
        try:
            logging.info(f"Login attempt: {attempt + 1}/{max_retries}")
            driver.get(SAP_URL)

            # Attempt to switch to a frame if required.
            try:
                WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.ID, "frameID"))
                )
                logging.info("Switched to frame (if present).")
            except TimeoutException:
                logging.info("No frame found, proceeding without switching.")

            # Ensure the page body is loaded.
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(1)  # Allow extra time for dynamic content

            # Locate username field and enter username
            logging.info("Waiting for username field...")
            username_field = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            logging.info("Username field found. Sending keys.")
            username_field.clear()
            username_field.send_keys(SAP_USERNAME)

            # Locate password field and enter password
            logging.info("Waiting for password field...")
            password_field = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            logging.info("Password field found. Sending keys.")
            password_field.clear()
            password_field.send_keys(SAP_PASSWORD)

            # Locate and click the Sign In button using multiple locators.
            logging.info("Waiting for Sign In button...")
            sign_in_button = None
            try:
                sign_in_button = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.ID, "signIn"))
                )
                logging.info("Sign In button found by ID.")
            except TimeoutException:
                logging.info("Sign In button not found by ID, trying XPath.")
                try:
                    sign_in_button = WebDriverWait(driver, 60).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]"))
                    )
                    logging.info("Sign In button found by XPath.")
                except TimeoutException:
                    logging.info("Sign In button not found by XPath, trying CSS Selector.")
                    try:
                        sign_in_button = WebDriverWait(driver, 60).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
                        )
                        logging.info("Sign In button found by CSS Selector.")
                    except TimeoutException:
                        logging.info("Sign In button not found by CSS Selector, trying Name.")
                        try:
                            sign_in_button = WebDriverWait(driver, 60).until(
                                EC.element_to_be_clickable((By.NAME, "loginButton"))
                            )
                            logging.info("Sign In button found by Name.")
                        except TimeoutException:
                            logging.error("Sign In button not found using any locator.")
                            raise NoSuchElementException("Failed to locate Sign In button using any locator.")

            if sign_in_button:
                logging.info("Clicking the Sign In button.")
                driver.execute_script("arguments[0].click();", sign_in_button)
            else:
                raise NoSuchElementException("Sign In button not located.")

            # Post-login verification
            logging.info("Waiting for post-login verification...")
            WebDriverWait(driver, 120).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sap-main-content")),
                    EC.presence_of_element_located((By.ID, "error-message")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".error")),
                    EC.title_contains("Error"),
                )
            )

            # Check for error indicators on the page.
            if "error" in driver.page_source.lower() or "failed" in driver.page_source.lower():
                logging.error("Login failed: Error message found on page.")
                driver.save_screenshot("login_error_page.png")
                raise WebDriverException("Login failed due to error message on page.")

            if "Sign In" in driver.title:
                logging.error("Login failed: Still on the Sign In page.")
                driver.save_screenshot("login_error_signin_page.png")
                raise WebDriverException("Login failed: Still on the Sign In page after login attempt.")

            logging.info("Login successful.")
            return  # Exit the function on success

        except (TimeoutException, NoSuchElementException, ElementNotInteractableException,
                StaleElementReferenceException, WebDriverException) as e:
            logging.error(f"Login failure: {str(e)}")
            screenshot_name = f"login_failure_attempt_{attempt + 1}.png"
            driver.save_screenshot(screenshot_name)
            logging.error(f"Screenshot saved as {screenshot_name}")
            logging.error(f"Page source at error (first 1000 chars): {driver.page_source[:1000]}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying login in {retry_delay} seconds...")
                time.sleep(retry_delay)
                driver.refresh()
            else:
                raise
        except NoSuchFrameException as e:
            logging.error(f"NoSuchFrameException: {e}")
            screenshot_name = f"frame_exception_{attempt + 1}.png"
            driver.save_screenshot(screenshot_name)
            logging.error(f"Screenshot saved as {screenshot_name}")
            logging.error(f"Page source at error (first 1000 chars): {driver.page_source[:1000]}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying login in {retry_delay} seconds...")
                time.sleep(retry_delay)
                driver.refresh()
            else:
                raise

def initialize_driver():
    """Initializes the Chrome WebDriver using webdriver_manager with a unique user data directory."""
    options = webdriver.ChromeOptions()
    # Add any options required for your environment (e.g., headless)
    options.add_argument("--start-maximized")
    # Generate a unique temporary directory for Chrome user data to avoid conflicts.
    user_data_dir = tempfile.mkdtemp(prefix="chrome_userdata_")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    logging.info(f"Using unique Chrome user data directory: {user_data_dir}")
    # Uncomment the following line if you want to run in headless mode:
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )
    return driver

def main():
    driver = None
    try:
        driver = initialize_driver()
        perform_login(driver)
        # Add further actions after successful login if needed.
        logging.info("Proceeding with post-login automation tasks...")
        # Example: navigate to a specific page, extract data, etc.
        # driver.get("https://sap.example.com/some_page")
        time.sleep(5)  # Pause for demonstration; replace with actual tasks.
    except Exception as ex:
        logging.error(f"Automation job failed: {ex}")
    finally:
        if driver:
            driver.quit()
        logging.info("Driver closed. Automation job completed.")

if __name__ == "__main__":
    main()
