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
import os
from dotenv import load_dotenv

# Load environment variables from .env file (ensure you have one)
load_dotenv()

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get credentials from environment variables (ensure these are set in your .env)
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Function to initialize the WebDriver
def init_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Comment out this line if you want to see the browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize the WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logger.info("WebDriver initialized successfully.")
        return driver
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {e}")
        raise

# Function to perform the login
def login_to_sap(driver):
    try:
        logger.info("Navigating to SAP login page.")
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=")
        
        # Wait for the username field to be visible and enter SAP username
        username_field = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "username")))  # Replace with actual ID if needed
        username_field.send_keys(SAP_USERNAME)
        logger.info("Entered SAP username.")
        
        # Wait for the password field to be visible and enter SAP password
        password_field = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "password")))  # Replace with actual ID if needed
        password_field.send_keys(SAP_PASSWORD)
        logger.info("Entered SAP password.")
        
        # Wait for the login button and click it
        login_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))  # Adjust XPATH as needed
        login_button.click()
        logger.info("Clicked on the login button.")
        
        # Wait for a successful login indication, for example, the user dashboard
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "dashboard")))  # Replace with actual element on successful login page
        logger.info("Logged in successfully.")

    except Exception as e:
        logger.error(f"Error during SAP login process: {e}")
        driver.quit()
        raise

# Main function to execute the automation process
def main():
    try:
        # Initialize the WebDriver
        driver = init_driver()
        
        # Perform the login
        login_to_sap(driver)
        
        # Here you can continue with other steps if necessary (e.g., job application, navigation, etc.)
        
    except Exception as e:
        logger.error(f"Automation process failed: {e}")
    finally:
        logger.info("Closing WebDriver.")
        driver.quit()

if __name__ == "__main__":
    main()
