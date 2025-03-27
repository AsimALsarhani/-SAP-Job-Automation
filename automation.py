import os
import time
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Environment variable configuration (update with your actual credentials and URL)
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = "asimalsarhani@gmail.com"

# Provide a valid, resolvable SAP login URL (update this value)
SAP_URL = os.environ.get("SAP_URL", "https://your.sap.login.page")

# Email SMTP configuration (for Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Remove for debugging
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver with ChromeDriverManager using Service and Options
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_url_with_retry(url, retries=3, delay=5):
    """
    Attempt to access the given URL with retry logic.
    """
    attempt = 0
    while attempt < retries:
        try:
            driver.get(url)
            return True
        except WebDriverException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(delay)
    return False

try:
    # Attempt to access the SAP login page with retry logic.
    if not get_url_with_retry(SAP_URL):
        raise Exception("Failed to access SAP URL after multiple attempts.")

    # --- Login Steps (update these selectors as needed) ---
    username_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(SAP_USERNAME)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(SAP_PASSWORD)

    login_button = driver.find_element(By.ID, "loginButton")
    login_button.click()

    # --- Wait for post-login page to load (update the selector as needed) ---
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "mainDashboard"))
    )

    # --- Click the "Save" Button (update the element ID as needed) ---
    save_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "saveButtonID"))
    )
    save_button.click()

    # Wait for the save process to complete (use explicit waits if possible)
    time.sleep(5)

    # --- Scroll to the Last Update Date Element (update the element ID as needed) ---
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "lastSaveTimeMsg"))
    )
    last_update_element = driver.find_element(By.ID, "lastSaveTimeMsg")
    
    # Scroll into view using ActionChains
    actions = ActionChains(driver)
    actions.move_to_element(last_update_element).perform()

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

    with open(screenshot_path, "rb") as img_file:
        img_data = img_file.read()
    msg.add_attachment(img_data, maintype="image", subtype="png", filename="last_update.png")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

finally:
    driver.quit()
