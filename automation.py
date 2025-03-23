import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SAP URL – update this to the correct URL for your SAP login page
SAP_URL = "https://sap-login-page-url.com"

# Retrieve environment variables
SAP_USERNAME = os.environ.get("SAP_USERNAME")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
    logger.error("Missing one or more required environment variables: SAP_USERNAME, SAP_PASSWORD, EMAIL_PASSWORD")
    exit(1)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def navigate_to_sap_login(driver):
    """Navigate to the SAP login page with retry on DNS resolution errors."""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            logger.info("Navigating to SAP login page: %s", SAP_URL)
            driver.get(SAP_URL)
            
            # If navigation succeeds, wait a bit for the page to load.
            time.sleep(5)
            
            # Check that the page title is non-empty as a basic indicator the page loaded.
            if driver.title:
                logger.info("Page loaded with title: %s", driver.title)
            else:
                logger.warning("Page loaded but title is empty.")
            return  # Exit the function if no exception
        except WebDriverException as e:
            if 'ERR_NAME_NOT_RESOLVED' in str(e):
                retries += 1
                logger.error("DNS resolution error encountered (attempt %d/%d). Retrying in %d seconds...", retries, MAX_RETRIES, RETRY_DELAY)
                time.sleep(RETRY_DELAY)
            else:
                logger.error("WebDriverException encountered: %s", e)
                raise e
    raise Exception("Failed to resolve DNS after multiple retries.")

def login_to_sap(driver):
    """Log in to the SAP SuccessFactors portal using explicit waits and logging."""
    try:
        navigate_to_sap_login(driver)

        # Update these XPaths based on your SAP login page. Use your browser's developer tools to verify.
        username_xpath = "//input[@id='username']"         # Replace with actual XPath
        password_xpath = "//input[@id='password']"         # Replace with actual XPath
        login_button_xpath = "//button[@id='loginBtn']"    # Replace with actual XPath
        success_xpath = "//div[@id='dashboard']"           # Replace with an element that confirms a successful login

        # Wait for the username field and enter username
        username_field = WebDriverWait(driver, 90).until(
            EC.visibility_of_element_located((By.XPATH, username_xpath))
        )
        logger.info("Username field located.")
        username_field.send_keys(SAP_USERNAME)
        logger.info("Entered SAP username.")

        # Wait for the password field and enter password
        password_field = WebDriverWait(driver, 90).until(
            EC.visibility_of_element_located((By.XPATH, password_xpath))
        )
        logger.info("Password field located.")
        password_field.send_keys(SAP_PASSWORD)
        logger.info("Entered SAP password.")

        # Wait for the login button to be clickable and click it
        login_button = WebDriverWait(driver, 90).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        logger.info("Login button is clickable.")
        login_button.click()
        logger.info("Clicked on the login button.")

        # Wait for an element that indicates a successful login
        WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.XPATH, success_xpath))
        )
        logger.info("Logged in successfully.")

    except (TimeoutException, NoSuchElementException) as e:
        logger.error("Element error during login: %s", e)
        logger.error("Page source snippet: %s", driver.page_source[:1000])
        driver.quit()
        raise e
    except Exception as e:
        logger.error("Error during SAP login process: %s", e)
        try:
            logger.error("Page source snippet: %s", driver.page_source[:1000])
        except Exception:
            logger.error("Could not retrieve page source.")
        driver.quit()
        raise e

def main():
    try:
        logger.info("Starting automation script.")
        
        # Configure Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Set up Chrome driver with webdriver-manager
        chrome_service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=options)
        
        login_to_sap(driver)
        
        # Example: take a screenshot after login
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        logger.info("Screenshot saved to %s", screenshot_path)
        
        # Add further automation steps as needed...
        
        driver.quit()
        logger.info("Automation script completed successfully.")
    except Exception as e:
        logger.error("Automation script failed.")
        exit(1)

if __name__ == "__main__":
    main()
