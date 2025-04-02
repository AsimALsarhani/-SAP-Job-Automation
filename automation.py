import os
import time
import logging
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def initialize_browser():
    """Initialize the Chrome WebDriver."""
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    logging.info("Browser initialized successfully")
    return driver

def perform_login(driver):
    """
    Performs the login actions.
    Expects the driver to be already initialized.
    """
    try:
        # Use SAP_URL from environment variables (must be set as a secret)
        sap_url = os.environ.get("SAP_URL", "https://example.com/login")
        driver.get(sap_url)
        logging.info("Login page loaded successfully")
        
        # Wait for the username field and perform login
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(os.environ.get("SAP_USERNAME", "your-username"))
        
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(os.environ.get("SAP_PASSWORD", "your-password"))
        
        # Wait for and click the "Sign In" button
        sign_in_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "signIn"))
        )
        sign_in_button.click()
        logging.info("Login action performed successfully")
        
        # Optionally, wait until a post-login element appears (adjust selector as needed)
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "mainDashboard"))
        )
        logging.info("Post-login dashboard loaded successfully")
    except Exception as e:
        logging.error(f"Login interaction failed: {e}")
        raise Exception("Login failed") from e

def send_email_with_screenshot(screenshot_path):
    """Sends an email with the given screenshot attached."""
    try:
        msg = EmailMessage()
        msg["Subject"] = "SAP Job Automation - Screenshot"
        msg["From"] = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
        msg["To"] = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")
        msg.set_content("Attached is the screenshot from SAP Job Automation.")
        
        with open(screenshot_path, "rb") as f:
            img_data = f.read()
        msg.add_attachment(img_data, maintype="image", subtype="png", filename="screenshot.png")
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.environ.get("SENDER_EMAIL"), os.environ.get("EMAIL_PASSWORD"))
            server.send_message(msg)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Sending email failed: {e}")
        raise

def main():
    driver = None
    try:
        driver = initialize_browser()
        perform_login(driver)
        
        # (Optional) Additional steps can be inserted here.
        # For example: click a "Save" button, capture a screenshot, etc.
        
        # Capture a screenshot after login
        screenshot_path = "screenshot.png"
        time.sleep(5)  # Allow any dynamic content to load
        driver.save_screenshot(screenshot_path)
        logging.info("Screenshot captured")
        
        send_email_with_screenshot(screenshot_path)
    except Exception as e:
        logging.error(f"Main execution failed: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Browser terminated")

if __name__ == "__main__":
    main()
