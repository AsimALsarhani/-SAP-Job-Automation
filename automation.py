import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve sensitive information from environment variables
SAP_USERNAME = os.getenv("SAP_USERNAME")  # Set your SAP username as an environment variable
SAP_PASSWORD = os.getenv("SAP_PASSWORD")  # Set your SAP password as an environment variable
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Set your email password as an environment variable

# Check if sensitive environment variables are set
if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
    logger.error("Environment variables for SAP_USERNAME, SAP_PASSWORD, and EMAIL_PASSWORD must be set.")
    exit(1)

# Use options for the Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Running headless (no browser UI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")  # Enable debugging port for connection issues

# Set up Chrome WebDriver
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    logger.info("WebDriver initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize WebDriver: {e}")
    exit(1)

# Open the SAP Login page
def login_to_sap():
    try:
        logger.info("Navigating to SAP login page.")
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=")
        
        # Wait for the username field to be visible and enter SAP username
        username_field = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "username")))  # Replace with actual ID if needed
        username_field.send_keys(SAP_USERNAME)
        logger.info("Entered SAP username.")
        
        # Wait for the password field to be visible and enter SAP password
        password_field = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "password")))  # Replace with actual ID if needed
        password_field.send_keys(SAP_PASSWORD)
        logger.info("Entered SAP password.")
        
        # Wait for the login button and click it
        login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))  # Adjust XPATH as needed
        login_button.click()
        logger.info("Clicked on the login button.")
        
    except Exception as e:
        logger.error(f"Error during SAP login process: {e}")
        driver.quit()
        raise

# Wait for the next page to load after login
def wait_for_next_page():
    try:
        logger.info("Waiting for the next page to load.")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "next_page_element_id")))  # Replace with actual ID
        logger.info("Next page loaded.")
    except Exception as e:
        logger.error(f"Error while waiting for the next page: {e}")
        driver.quit()
        raise

# Perform a specific SAP task after login
def perform_sap_task():
    try:
        logger.info("Performing SAP task.")
        
        # Replace with actual step to interact with SAP
        task_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='task_button_id']")))  # Adjust XPATH
        task_button.click()
        
        logger.info("Task completed successfully.")
        
    except Exception as e:
        logger.error(f"Error while performing SAP task: {e}")
        driver.quit()
        raise

# Handle email login (if required)
def login_to_email():
    try:
        logger.info("Logging into email.")
        # Assuming you're using Gmail as an example
        driver.get("https://mail.google.com")
        
        # Wait for the email input field, enter email password
        email_field = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "identifierId")))
        email_field.send_keys(SAP_USERNAME)
        
        next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='identifierNext']")))
        next_button.click()
        
        # Wait for password field and enter password
        password_field = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, "password")))
        password_field.send_keys(EMAIL_PASSWORD)
        
        next_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='passwordNext']")))
        next_button.click()
        
        logger.info("Logged into email successfully.")
        
    except Exception as e:
        logger.error(f"Error during email login: {e}")
        driver.quit()
        raise

# Main function to orchestrate everything
def main():
    try:
        login_to_sap()
        wait_for_next_page()
        perform_sap_task()
        login_to_email()
        
    except Exception as e:
        logger.error(f"Automation failed: {e}")
    finally:
        logger.info("Automation process completed.")
        driver.quit()

if __name__ == "__main__":
    main()
