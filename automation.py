from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Load credentials
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Setup WebDriver
driver = webdriver.Chrome()

try:
    # Open SAP SuccessFactors login page
    driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true")

    # Wait for page to load
    time.sleep(5)

    # Enter username and password
    username_field = driver.find_element(By.ID, "username")  # Replace with actual ID
    password_field = driver.find_element(By.ID, "password")  # Replace with actual ID
    username_field.send_keys(SAP_USERNAME)
    password_field.send_keys(SAP_PASSWORD)

    # Click the "Sign In" button
    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
    )
    sign_in_button.click()

    # Wait for login to complete
    time.sleep(5)

    # Click "Save" button (adjust selector if needed)
    save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
    save_button.click()

    # Wait for save to complete
    time.sleep(5)

    # Refresh page
    driver.refresh()
    time.sleep(3)

finally:
    driver.quit()

print("Automation Completed Successfully.")
