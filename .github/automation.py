from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

# Load credentials from GitHub Secrets
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Set up Selenium WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")  # Run in background
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Open SAP SuccessFactors Login Page
    driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true")

    time.sleep(5)  # Wait for the page to load

    # Enter username
    username_field = driver.find_element(By.ID, "username")  # Replace with actual ID
    username_field.send_keys(SAP_USERNAME)

    # Enter password
    password_field = driver.find_element(By.ID, "password")  # Replace with actual ID
    password_field.send_keys(SAP_PASSWORD)

    # Click login button
    login_button = driver.find_element(By.ID, "loginButton")  # Replace with actual ID
    login_button.click()

    time.sleep(5)  # Wait for login to complete

    # Click "Save" button
    save_button = driver.find_element(By.ID, "saveButton")  # Change if needed
    save_button.click()

    time.sleep(5)  # Wait for saving to complete

    # Refresh Page
    driver.refresh()

    time.sleep(3)  # Wait after refresh

finally:
    driver.quit()  # Close browser

print("Automation Completed Successfully.")
