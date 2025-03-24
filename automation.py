import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Retrieve credentials from environment variables
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Email password for sending email
SAP_USERNAME = os.getenv("SAP_USERNAME")  # SAP login username
SAP_PASSWORD = os.getenv("SAP_PASSWORD")  # SAP login password
FROM_EMAIL = "mshtag1990@gmail.com"  # Sender's email
TO_EMAIL = "asimalsarhani@gmail.com"  # Recipient email

# Check if credentials are available
if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
    logging.error("❌ Missing SAP credentials or email password! Check environment variables.")
    exit(1)

# Configure WebDriver options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run headless for background operation
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--remote-debugging-port=9222")

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)  # Explicit wait

try:
    # Step 1: Navigate to SAP SuccessFactors login page
    logging.info("🚀 Navigating to SAP SuccessFactors login page...")
    driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=#skipContent")

    # Step 2: Log in to SAP SuccessFactors
    logging.info("🔐 Logging in to SAP SuccessFactors...")
    
    username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
    password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
    
    username_field.send_keys(SAP_USERNAME)
    password_field.send_keys(SAP_PASSWORD)
    
    login_button = wait.until(EC.element_to_be_clickable((By.ID, "loginButton")))
    login_button.click()

    # Wait for the dashboard or confirmation element to appear
    wait.until(EC.presence_of_element_located((By.ID, "dashboard")))  # Update with actual dashboard ID if different

    logging.info("✅ Login successful!")

    # Step 3: Scroll to the bottom of the page and click "Save" button
    logging.info("📜 Scrolling to the bottom of the page to click 'Save' button...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Save')]")))
    save_button.click()

    # Step 4: Scroll to the top and click on a blank area
    logging.info("🔝 Scrolling to the top of the page and clicking on a blank area...")
    driver.execute_script("window.scrollTo(0, 0);")
    driver.find
