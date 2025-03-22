import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SAP SuccessFactors login URL
SAP_URL = 'https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg='

# Credentials (ensure these are set in your environment variables)
SAP_USERNAME = os.getenv('SAP_USERNAME')
SAP_PASSWORD = os.getenv('SAP_PASSWORD')

def setup_driver():
    """Set up the Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def login_to_sap(driver):
    """Perform login to SAP SuccessFactors."""
    try:
        driver.get(SAP_URL)
        logger.info('Navigated to SAP login page.')

        # Wait for the username field to be present and enter the username
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        username_field.send_keys(SAP_USERNAME)
        logger.info('Entered username.')

        # Enter the password
        password_field = driver.find_element(By.NAME, 'password')
        password_field.send_keys(SAP_PASSWORD)
        logger.info('Entered password.')

        # Click the login button
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()
        logger.info('Clicked login button.')

        # Wait for the login to complete by checking for a post-login element
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'post-login-element-id'))  # Replace with actual element ID
        )
        logger.info('Login successful.')

    except TimeoutException:
        logger.error('Login failed: Timeout while waiting for page elements.')
    except NoSuchElementException as e:
        logger.error(f'Login failed: Element not found. {e}')
    except Exception as e:
        logger.error(f'An unexpected error occurred during login: {e}')

def main():
    driver = setup_driver()
    try:
        login_to_sap(driver)
        # Add further automation steps here
    finally:
        driver.quit()
        logger.info('WebDriver session closed.')

if __name__ == '__main__':
    main()
