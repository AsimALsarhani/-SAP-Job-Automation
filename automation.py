import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert

# Read environment variables for sensitive data
SAP_USERNAME = os.getenv('SAP_USERNAME')
SAP_PASSWORD = os.getenv('SAP_PASSWORD')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Set up Chrome WebDriver with options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the Chrome WebDriver
service = Service('/path/to/chromedriver')  # Ensure this path points to your chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

def login_to_sap():
    try:
        # Navigate to SAP login page
        driver.get("https://sap.example.com/login")

        # Find username field and enter the SAP username
        username_field = driver.find_element(By.XPATH, "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/div/div[2]/div/div/table/tbody/tr[1]/td[2]/input")
        username_field.send_keys(SAP_USERNAME)

        # Find password field and enter the SAP password
        password_field = driver.find_element(By.XPATH, "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[2]/div/div/div[2]/div/div/table/tbody/tr[2]/td[2]/div/input[1]")
        password_field.send_keys(SAP_PASSWORD)

        # Submit the login form
        password_field.send_keys(Keys.RETURN)

        # Wait for the login to complete and the main page to load
        time.sleep(5)

    except Exception as e:
        print(f"Error during SAP login: {e}")
        driver.quit()
        sys.exit(1)

def perform_task_in_sap():
    try:
        # Example: Locate a specific SAP element and interact with it
        task_button = driver.find_element(By.XPATH, "/path/to/task/button")
        task_button.click()

        # Handle any alerts that pop up
        try:
            alert = Alert(driver)
            alert.accept()  # Accept the alert if it appears
        except:
            pass

        # Wait for the task to complete (this could vary depending on the task you're automating)
        time.sleep(10)

    except Exception as e:
        print(f"Error performing task in SAP: {e}")
        driver.quit()
        sys.exit(1)

def logout_from_sap():
    try:
        # Example: Find the logout button and click it
        logout_button = driver.find_element(By.XPATH, "/path/to/logout/button")
        logout_button.click()

        # Wait for the logout to complete
        time.sleep(3)

    except Exception as e:
        print(f"Error logging out from SAP: {e}")
        driver.quit()
        sys.exit(1)

def main():
    # Step 1: Log in to SAP
    login_to_sap()

    # Step 2: Perform the task in SAP
    perform_task_in_sap()

    # Step 3: Log out from SAP
    logout_from_sap()

    # Step 4: Close the browser after completing the task
    driver.quit()

if __name__ == "__main__":
    main()
