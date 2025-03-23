import time
import smtplib
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Load environment variables
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SENDER = "mshtag1990@gmail.com"
EMAIL_RECEIVER = "asimalsarhani@gmail.com"

# Configure WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")  # Path to chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

def login_to_sap():
    driver.get("https://sap-portal-url.com")  # Replace with actual SAP URL
    time.sleep(5)

    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.ID, "loginButton")

    username_input.send_keys(SAP_USERNAME)
    password_input.send_keys(SAP_PASSWORD)
    login_button.click()
    time.sleep(50)  # Wait for 50 seconds

def navigate_and_save():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    save_button = driver.find_element(By.ID, "saveButton")  # Adjust this selector
    save_button.click()
    time.sleep(55)

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)

    blank_area = driver.find_element(By.ID, "header")  # Adjust selector
    blank_area.click()
    time.sleep(10)

def take_screenshot():
    screenshot_path = "screenshot.png"
    driver.save_screenshot(screenshot_path)
    return screenshot_path

def send_email(screenshot_path):
    subject = "SAP Automation Screenshot"
    body = "Attached is the screenshot from the SAP automation."
    message = f"Subject: {subject}\n\n{body}"

    with open(screenshot_path, "rb") as file:
        attachment = file.read()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message, attachment)

try:
    login_to_sap()
    navigate_and_save()
    screenshot = take_screenshot()
    send_email(screenshot)
    print("Automation successful!")
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
