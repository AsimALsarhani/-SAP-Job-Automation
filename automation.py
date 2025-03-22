import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging with timestamp
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Retrieve credentials from environment variables (ensure these are set in your environment/CI/CD secrets)
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Not used here, but available if needed

if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
    logger.error("Missing required environment variables: SAP_USERNAME, SAP_PASSWORD, EMAIL_PASSWORD")
    raise ValueError("Missing credentials")

def login_to_sap(driver):
    try:
        logger.info("Navigating to SAP login page.")
        # Use the full SAP login URL provided
        url = ("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&"
               "company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=")
        driver.get(url)
        time.sleep(5)  # Allow page to load

        logger.info("Page loaded. Title: " + driver.title)
        
        # Use provided XPath for the username field
        username_xpath = (
            "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/"
            "div/div[2]/div/div/table/tbody/tr[1]/td[2]/input"
        )
        username_field = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, username_xpath))
        )
        logger.info("Username field located.")
        username_field.send_keys(SAP_USERNAME)
        logger.info("SAP username entered.")
        
        # Use provided XPath for the password field
        password_xpath = (
            "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/"
            "div/div[2]/div/div/table/tbody/tr[2]/td[2]/div/input[1]"
        )
        password_field = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, password_xpath))
        )
        logger.info("Password field located.")
        password_field.send_keys(SAP_PASSWORD)
        logger.info("SAP password entered.")
        
        # Wait for the login button to be clickable and click it
        login_button_xpath = "//button[@type='submit']"
        login_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        logger.info("Login button is clickable.")
        login_button.click()
        logger.info("Login button clicked.")
        
        # Wait for an element that confirms a successful login (update the XPath as needed)
        success_xpath = "//div[@id='dashboard']"  # Example element; adjust for your SAP page
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, success_xpath))
        )
        logger.info("Logged in successfully.")
        
    except Exception as e:
        logger.error(f"Error during SAP login process: {e}")
        # Log a snippet of the page source to help diagnose the issue
        logger.error("Page source snippet: " + driver.page_source[:500])
        driver.quit()
        raise

def main():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.headless = True  # Set to False for debugging (visible browser)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Use webdriver_manager to automatically install the correct ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        login_to_sap(driver)
    finally:
        driver.quit()
        logger.info("WebDriver closed.")

if __name__ == "__main__":
    main()
