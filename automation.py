import os
import time
import smtplib
import logging
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Email credentials (Use environment variables for security)
EMAIL_SENDER = "mshtag1990@gmail.com"
EMAIL_RECEIVER = "asimalsarhani@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Store this securely

# SAP credentials (Use environment variables for security)
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
SAP_LOGIN_URL = "https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05"

# Setup WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run without opening a browser
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def login():
    """Logs into the SAP SuccessFactors portal."""
    try:
        logging.info("Navigating to SAP login page...")
        driver.get(SAP_LOGIN_URL)
        time.sleep(3)

        # Locate username and password fields
        username_field = driver.find_element(By.ID, "username")  # Update ID if needed
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "login")

        # Enter credentials
        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)
        login_button.click()
        
        logging.info("Successfully logged in.")
        time.sleep(50)  # Wait for 50 seconds

    except Exception as e:
        logging.error(f"Login failed: {e}")
        driver.quit()
        exit(1)

def scroll_and_save():
    """Scrolls to the bottom and clicks 'Save'."""
    try:
        logging.info("Scrolling to the bottom and clicking 'Save'...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        save_button = driver.find_element(By.ID, "saveButton")  # Update ID if needed
        save_button.click()

        logging.info("Clicked 'Save'. Waiting 55 seconds...")
        time.sleep(55)

    except Exception as e:
        logging.error(f"Failed to click 'Save': {e}")
        driver.quit()
        exit(1)

def scroll_and_click_blank():
    """Scrolls to the top and clicks a blank area."""
    try:
        logging.info("Scrolling to the top...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(3)

        blank_area = driver.find_element(By.TAG_NAME, "body")  # Adjust selector if needed
        ActionChains(driver).move_to_element(blank_area).click().perform()
        
        logging.info("Clicked on a blank area. Waiting 10 seconds...")
        time.sleep(10)

    except Exception as e:
        logging.error(f"Failed to click blank area: {e}")
        driver.quit()
        exit(1)

def take_screenshot():
    """Takes a screenshot and saves it."""
    screenshot_path = "screenshot.png"
    try:
        logging.info("Taking a screenshot...")
        driver.save_screenshot(screenshot_path)
        logging.info(f"Screenshot saved at {screenshot_path}")
        return screenshot_path

    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")
        driver.quit()
        exit(1)

def send_email(screenshot_path):
    """Sends an email with the screenshot."""
    try:
        logging.info("Preparing email...")
        msg = EmailMessage()
        msg["Subject"] = "SAP Automation Screenshot"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg.set_content("Attached is the screenshot from SAP automation.")

        with open(screenshot_path, "rb") as file:
            msg.add_attachment(file.read(), maintype="image", subtype="png", filename="screenshot.png")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logging.info("Email sent successfully.")

    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        exit(1)

# Run the automation
try:
    login()
    scroll_and_save()
    scroll_and_click_blank()
    screenshot = take_screenshot()
    send_email(screenshot)
finally:
    driver.quit()
    logging.info("Automation complete.")
