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
from selenium.common.exceptions import TimeoutException

# Configure logging with timestamps
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Retrieve credentials from environment variables
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Not used here, but required to be set

if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
    logger.error("Missing one or more required environment variables: SAP_USERNAME, SAP_PASSWORD, EMAIL_PASSWORD")
    raise ValueError("Missing credentials")

# SAP login URL (provided)
SAP_URL = ("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&"
           "company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=")

def setup_driver():
    """Set up the Chrome WebDriver with a unique user data directory."""
    chrome_options = Options()
    chrome_options.headless = True  # Change to False for debugging (visible browser)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Create a unique temporary user-data-dir to avoid conflicts
    unique_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={unique_dir}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login_to_sap(driver):
    """Perform SAP login using explicit waits and provided XPATHs."""
    try:
        logger.info("Navigating to SAP login page.")
        driver.get(SAP_URL)
        time.sleep(5)  # Allow page to load
        
        logger.info("Page title: " + driver.title)
        
        # Provided XPATH for username field
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
        
        # Provided XPATH for password field
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
        
        # Click the login button
        login_button_xpath = "//button[@type='submit']"
        login_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        logger.info("Login button is clickable.")
        login_button.click()
        logger.info("Clicked on the login button.")
        
        # Wait for an element that confirms a successful login
        success_xpath = "//div[@id='dashboard']"  # Replace with an element unique to the logged-in page
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, success_xpath))
        )
        logger.info("Logged in successfully.")
        
    except TimeoutException as te:
        logger.error("Timeout while waiting for page elements during login.")
        logger.error("Page source snippet: " + driver.page_source[:1000])
        driver.quit()
        raise te
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
        # Additional automation steps can be added here.
    finally:
        driver.quit()
        logger.info("WebDriver closed.")

if __name__ == "__main__":
    main()
