import os
import time
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Original environment variable configuration
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = "asimalsarhani@gmail.com"

# Email SMTP configuration (for Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode if needed
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver using ChromeDriverManager with options and service
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Open SAP login page
    driver.get("https://your.sap.login.page")  # Update with your SAP URL

    # --- Login Steps (update these selectors as needed) ---
    username_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(SAP_USERNAME)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(SAP_PASSWORD)

    login_button = driver.find_element(By.ID, "loginButton")
    login_button.click()

    # --- Wait for post-login page to load ---
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "mainDashboard"))
    )

    # --- Click the "Save" Button ---
    save_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "saveButtonID"))  # Replace with actual ID
    )
    save_button.click()

    # Wait for the save process to complete (prefer explicit wait if available)
    time.sleep(5)

    # --- Scroll to the Last Update Date Element ---
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "lastSaveTimeMsg"))
    )
    last_update_element = driver.find_element(By.ID, "lastSaveTimeMsg")
    
    # Scroll into view using ActionChains
    actions = ActionChains(driver)
    actions.move_to_element(last_update_element).perform()

    # If clicking is necessary to reveal the full date info, uncomment the next line:
    # last_update_element.click()

    # Allow any dynamic content to update
    time.sleep(2)

    # --- Capture Screenshot ---
    screenshot_path = "last_update.png"
    driver.save_screenshot(screenshot_path)

    # --- Send Email with Screenshot Attached ---
    msg = EmailMessage()
    msg["Subject"] = "SAP Job Automation - Last Update Screenshot"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg.set_content("Attached is the screenshot showing the last update.")

    # Attach the screenshot file
    with open(screenshot_path, "rb") as img_file:
        img_data = img_file.read()
    msg.add_attachment(img_data, maintype="image", subtype="png", filename="last_update.png")

    # Connect to SMTP server and send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

finally:
    driver.quit()
