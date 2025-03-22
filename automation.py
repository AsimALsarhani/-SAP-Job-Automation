import time
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# EMAIL SETTINGS
SENDER_EMAIL = "Mshtag1990@gmail.com"
RECEIVER_EMAIL = "Asimalsarhani@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Use environment variable for security
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# SAP LOGIN CREDENTIALS
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Setup Chrome Options
options = Options()
# options.add_argument("--headless")  # Uncomment for debugging
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Setup Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def automate_process():
    start_time = time.time()
    try:
        print("Opening SAP SuccessFactors...")
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true")
        time.sleep(5)

        print("Logging in...")
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)

        sign_in_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
        )
        sign_in_button.click()
        time.sleep(5)

        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Locate the Save button
        save_button_xpath = "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[1]/div[23]/div/span"
        save_button = WebDriverWait(driver, 15).until(
            EC.presence_of_e
