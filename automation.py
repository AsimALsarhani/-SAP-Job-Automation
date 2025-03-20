from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Load credentials
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Setup Chrome options
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-data-dir=/tmp/chrome-data")  # Use a unique temporary user data directory

# Setup Chrome WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Open the SAP SuccessFactors login page
    driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true")
    time.sleep(5)  # Wait for the page to load

    # Enter username and password
    username_field = driver.find_element(By.ID, "username")  # Replace with actual field ID if different
    password_field = driver.find_element(By.ID, "password")  # Replace with actual field ID if different
    username_field.send_keys(SAP_USERNAME)
    password_field.send_keys(SAP_PASSWORD)

    # Click the "Sign In" button using XPath based on button text
    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
    )
    sign_in_button.click()

    time.sleep(5)  # Wait for login to complete

    # Click "Save" button (update the selector as needed)
    save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
    save_button.click()

    time.sleep(5)  # Wait for saving to complete

    # Refresh page
    driver.refresh()
    time.sleep(3)

finally:
    driver.quit()

print("Automation Completed Successfully.")
