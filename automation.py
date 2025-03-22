import os
import time
import logging
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging with timestamps
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Retrieve credentials from environment variables
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Not used in this snippet but required to be set

if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
    logger.error("Missing one or more required environment variables: SAP_USERNAME, SAP_PASSWORD, or EMAIL_PASSWORD")
    raise ValueError("Missing credentials")

# SAP SuccessFactors login URL (provided)
SAP_URL = (
    "https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&"
    "company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg="
)

def setup_driver():
    """
    Set up the Chrome WebDriver using webdriver_manager.
    Create a unique temporary user-data directory to avoid conflicts.
    """
    chrome_options = Options()
    chrome_options.headless = True  # Change to False for debugging (visible browser)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Create a unique temporary directory for user-data-dir
    temp_profile = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_profile}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login_to_sap(driver):
    """Log in to the SAP SuccessFactors portal using explicit waits and detailed logging."""
    try:
        logger.info("Navigating to SAP login page.")
        driver.get(SAP_URL)
        time.sleep(5)  # Allow the page to load

        logger.info("Page title: " + driver.title)

        # Provided XPath for the username field (verify using Developer Tools)
        username_xpath = (
            "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/"
            "div/div[2]/div/div/table/tbody/tr[1]/td[2]/input"
        )
        username_field = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, username_xpath))
        )
        logger.info("Username field located.")
        username_field.send_keys(SAP_USERNAME)
        logger.info("Entered SAP username.")

        # Provided XPath for the password field (verify using Developer Tools)
        password_xpath = (
            "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/"
            "div/div[2]/div/div/table/tbody/tr[2]/td[2]/div/input[1]"
        )
        password_field = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, password_xpath))
        )
        logger.info("Password field located.")
        password_field.send_keys(SAP_PASSWORD)
        logger.info("Entered SAP password.")

        # Click the login button using its XPath (verify this locator)
        login_button_xpath = "//button[@type='submit']"
        login_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        logger.info("Login button is clickable.")
        login_button.click()
        logger.info("Clicked on the login button.")

        # Wait for an element that confirms a successful login (update as needed)
        success_xpath = "//div[@id='dashboard']"  # Example; adjust to a unique element on your SAP page
        WebDriverWait(driver, 60).until(
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
    driver = setup_driver()
    try:
        login_to_sap(driver)
        # Additional automation steps can be added here if needed.
    finally:
        driver.quit()
        logger.info("WebDriver closed.")

if __name__ == "__main__":
    main()
