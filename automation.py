from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Update with your credentials
SAP_USERNAME = "your_sap_username"
SAP_PASSWORD = "your_sap_password"

def login_to_sap(driver):
    try:
        logger.info("Navigating to SAP login page.")
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=")

        # Wait for the username field to be visible and enter SAP username
        username_xpath = "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/div/div[2]/div/div/table/tbody/tr[1]/td[2]/input"
        username_field = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, username_xpath)))
        logger.info("Username field is visible.")
        username_field.send_keys(SAP_USERNAME)
        logger.info("Entered SAP username.")
        
        # Wait for the password field to be visible and enter SAP password
        password_xpath = "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/div/div[2]/div/div/table/tbody/tr[2]/td[2]/div/input[1]"
        password_field = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, password_xpath)))
        logger.info("Password field is visible.")
        password_field.send_keys(SAP_PASSWORD)
        logger.info("Entered SAP password.")
        
        # Wait for the login button and click it
        login_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))  # Update XPath if needed
        logger.info("Login button is clickable.")
        login_button.click()
        logger.info("Clicked on the login button.")
        
        # Wait for a successful login indication (example: dashboard element)
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@id='dashboard']")))  # Update to an actual element that confirms login
        logger.info("Logged in successfully.")
        
    except Exception as e:
        logger.error(f"Error during SAP login process: {e}")
        driver.quit()
        raise

# Main function to initialize WebDriver
def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True  # Set this to False for debugging (visible browser)
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        login_to_sap(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
