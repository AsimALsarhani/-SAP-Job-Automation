import os
import time
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Environment variable configuration (secrets from GitHub)
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")
SAP_URL = os.environ.get("SAP_URL")  # Must be set as a secret

if not SAP_URL:
    raise Exception("SAP_URL is not provided. Please set the SAP_URL environment variable.")

# Email SMTP configuration (Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Remove for debugging if needed
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver using ChromeDriverManager with Service and Options
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def access_url_with_retry(url, max_attempts=3, delay=5):
    """
    Attempts to access the given URL with retry logic.
    Verifies document.readyState is complete and that the login field (ID 'username') is present.
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            print(f"Attempt {attempt + 1}: accessing {url}")
            driver.get(url)
            time.sleep(3)  # Allow page to load
            ready_state = driver.execute_script("return document.readyState")
            print("Document ready state:", ready_state)
            if ready_state == "complete" and driver.find_elements(By.ID, "username"):
                print("Page loaded successfully, login field found.")
                return True
            else:
                print("Page not fully loaded or login field missing.")
        except WebDriverException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        attempt += 1
        time.sleep(delay)
    return False

try:
    # Access the SAP URL with retry logic.
    if not access_url_with_retry(SAP_URL):
        raise Exception("Failed to access SAP URL after multiple attempts.")

    # --- Login Steps ---
    username_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(SAP_USERNAME)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(SAP_PASSWORD)

    # Wait for the "Sign In" element using a robust XPath that looks for any element (button, input, or link)
    # containing the text "sign in" (ignoring case and spaces)
    sign_in_button = WebDriverWait(driver, 45).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(translate(normalize-space(string(.)), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]")
        )
    )
    print("Found sign in button, clicking it.")
    sign_in_button.click()

    # --- Wait for post-login page to load ---
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "mainDashboard"))
    )

    # --- Click the "Save" Button ---
    save_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "saveButtonID"))
    )
    save_button.click()

    # Wait for the save process to complete
    time.sleep(5)

    # --- Scroll to the Last Update Date Element ---
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "lastSaveTimeMsg"))
    )
    last_update_element = driver.find_element(By.ID, "lastSaveTimeMsg")
    actions = ActionChains(driver)
    actions.move_to_element(last_update_element).perform()
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

    with open(screenshot_path, "rb") as f:
        img_data = f.read()
    msg.add_attachment(img_data, maintype="image", subtype="png", filename="last_update.png")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

except TimeoutException as te:
    print("Timeout waiting for an element:", te)
    raise
except Exception as e:
    print("Error occurred:", e)
    raise
finally:
    driver.quit()
