import os
import logging
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Not used here, but must be set

if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
    logger.error("Missing one or more required environment variables: SAP_USERNAME, SAP_PASSWORD, EMAIL_PASSWORD")
    raise ValueError("Missing credentials")

# SAP SuccessFactors login URL (provided)
SAP_URL = (
    "https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&"
    "company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg="
)

def setup_driver():
    """
    Set up the Chrome WebDriver using webdriver_manager.
    Do not specify a fixed user-data-dir so that Chrome uses the default.
    """
    chrome_options = Options()
    chrome_options.headless = True  # Set to False for debugging (visible browser)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Do not force a user-data-dir to avoid conflicts.
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login_to_sap(driver):
    """
    Log in to the SAP SuccessFactors portal using explicit waits.
    """
    try:
        logger.info("Navigating to SAP login page.")
        driver.get(SAP_URL)
        time.sleep(5)  # Allow page to load

        # Provided XPath for the username field (verify this using browser dev tools)
        username_xpath = (
            "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/"
            "div/div[2]/div/div/table/tbody/tr[1]/td[2]/input"
        )
        username_field = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, username_xpath))
        )
        logger.info("Username field located.")
        username_field.send_keys(SAP_USERNAME)
        username_field.send_keys(Keys.RETURN)
        
        # Similarly, locate and enter the password (XPath for password field needed)
        password_xpath = (
            "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/"
            "div/div[2]/div/div/table/tbody/tr[2]/td[2]/input"
        )
        password_field = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, password_xpath))
        )
        logger.info("Password field located.")
        password_field.send_keys(SAP_PASSWORD)
        password_field.send_keys(Keys.RETURN)
        
        time.sleep(5)  # Allow page to load
        logger.info("Login successful.")
        
        # Verify successful login by checking for a specific element on the landing page
        success_element_xpath = "/html/body/div/success_indicator"
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, success_element_xpath))
        )
        logger.info("Login verification successful.")

    except Exception as e:
        logger.error(f"An error occurred during login: {e}")
        driver.quit()
        raise e

def main():
    driver = setup_driver()
    try:
        login_to_sap(driver)
        # Add further automation steps here
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
