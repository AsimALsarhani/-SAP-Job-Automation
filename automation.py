import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve credentials from environment variables
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

if not SAP_USERNAME or not SAP_PASSWORD:
    logger.error("Missing required credentials.")
    raise ValueError("SAP credentials are missing.")

def login_to_sap(driver):
    try:
        logger.info("Navigating to SAP login page.")
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05")

        username_xpath = "//input[@name='username']"
        password_xpath = "//input[@name='password']"
        login_button_xpath = "//button[@type='submit']"

        # Wait for the username field and enter SAP username
        username_field = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, username_xpath))
        )
        username_field.send_keys(SAP_USERNAME)
        logger.info("Entered SAP username.")

        # Wait for the password field and enter SAP password
        password_field = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, password_xpath))
        )
        password_field.send_keys(SAP_PASSWORD)
        logger.info("Entered SAP password.")

        # Click the login button
        login_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        login_button.click()
        logger.info("Clicked on login button.")

        # Wait for login success confirmation
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='dashboard']"))
        )
        logger.info("Successfully logged in.")

    except Exception as e:
        logger.error(f"Login failed: {e}")
        driver.quit()
        raise

def main():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Runs in headless mode (remove if debugging)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")  # Prevents user-data-dir issue

    # Use WebDriver Manager to manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        login_to_sap(driver)
    finally:
        driver.quit()
        logger.info("WebDriver session closed.")

if __name__ == "__main__":
    main()
