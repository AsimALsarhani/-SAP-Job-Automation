import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SAP URL (update this to your SAP SuccessFactors login page)
SAP_URL = "https://your-sap-successfactors-url.com"

# Retrieve required environment variables (exit if any are missing)
SAP_USERNAME = os.environ.get("SAP_USERNAME")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
    logger.error("One or more required environment variables (SAP_USERNAME, SAP_PASSWORD, EMAIL_PASSWORD) are missing.")
    exit(1)

def login_to_sap(driver):
    """Log in to the SAP SuccessFactors portal using explicit waits and logging."""
    try:
        logger.info("Navigating to SAP login page.")
        driver.get(SAP_URL)
        time.sleep(5)  # Allow the page to load

        logger.info("Page title: " + driver.title)
        
        # Update these XPaths by inspecting the SAP login page.
        username_xpath = "//input[@id='username']"           # Replace with actual XPath for username field
        password_xpath = "//input[@id='password']"           # Replace with actual XPath for password field
        login_button_xpath = "//button[@id='loginBtn']"      # Replace with actual XPath for login button
        success_xpath = "//div[@id='dashboard']"             # Replace with an element that confirms a successful login
        
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
        
    except TimeoutException as te:
        logger.error("Timeout while waiting for an element during login.")
        logger.error("Page source snippet: " + driver.page_source[:1000])
        driver.quit()
        raise te
    except NoSuchElementException as ne:
        logger.error(f"Element not found: {ne}")
        logger.error("Page source snippet: " + driver.page_source[:1000])
        driver.quit()
        raise ne
    except Exception as e:
        logger.error(f"Error during SAP login process: {e}")
        try:
            logger.error("Page source snippet: " + driver.page_source[:1000])
        except Exception:
            logger.error("Could not retrieve page source.")
        driver.quit()
        raise e

def main():
    try:
        logger.info("Starting automation script.")
        
        # Configure Chrome options for headless mode, incognito, etc.
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--incognito")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Set up the Chrome driver using webdriver-manager
        chrome_service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=options)
        
        # Log in to SAP
        login_to_sap(driver)
        
        # Take a screenshot after successful login
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}.")
        
        # Further actions (e.g., send email with screenshot) can be added here
        
        driver.quit()
        logger.info("Automation script completed successfully.")
    except Exception as e:
        logger.error("Automation script failed.")
        exit(1)

if __name__ == "__main__":
    main()
