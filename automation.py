import time  # Added to fix F821 undefined name 'time'
import logging
from logging.handlers import RotatingFileHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import tempfile
import smtplib

# Configure logging with rotation
log_handler = RotatingFileHandler(
    "selenium_debug.log", maxBytes=5 * 1024 * 1024, backupCount=5
)
logging.basicConfig(handlers=[log_handler], level=logging.ERROR)

# Retrieve credentials from environment variables
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = "asimalsarhani@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(screenshot_path):
    """Send an email with the screenshot attachment."""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = "SAP Job Portal Screenshot"

    body = MIMEText(
        "Please find attached the screenshot from the SAP job portal automation.",
        "plain"
    )
    msg.attach(body)

    with open(screenshot_path, "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header(
            "Content-Disposition",
            "attachment",
            filename=os.path.basename(screenshot_path)
        )
        msg.attach(img)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        logging.info(f"Email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def highlight_element(driver, element):
    """Highlights a Selenium WebElement by changing its border color via JavaScript."""
    driver.execute_script("arguments[0].style.border='3px solid red'", element)

def initialize_webdriver():
    """Initialize the Chrome WebDriver with options."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")

    # Use a unique user-data directory
    unique_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={unique_dir}")

    # Temporarily remove headless mode for debugging
    # options.add_argument("--headless")

    # Initialize WebDriver without specifying version
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

def sign_in(driver):
    """Sign in to the SAP portal."""
    SAP_SIGNIN_URL = (
        f"https://{SAP_USERNAME}:{SAP_PASSWORD}"
        "@career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05"
    )
    driver.get(SAP_SIGNIN_URL)
    logging.info("Navigating to SAP sign-in page...")

    # Wait for the login fields to be present
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    logging.info("Login fields detected on the page.")

    # Perform sign in
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    username_field.send_keys(SAP_USERNAME)
    password_field.send_keys(SAP_PASSWORD)
    sign_in_button = driver.find_element(
        By.XPATH, "//button[@data-testid='signInButton']"
    )
    sign_in_button.click()
    logging.info("Sign in button clicked.")

    # Wait for the URL to change after sign in
    WebDriverWait(driver, 60).until(EC.url_changes(SAP_SIGNIN_URL))
    logging.info("Sign in appears successful, URL changed to %s", driver.current_url)
    driver.save_screenshot("login_success.png")

def click_save_button(driver):
    """Click the save button and handle potential errors."""
    try:
        save_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='saveButton']"))
        )
        save_button.click()
        logging.info("Save button clicked.")
        driver.save_screenshot("save_clicked.png")
    except Exception as e:
        logging.error(f"Save button not found or not clickable: {e}")

def scroll_and_highlight_elements(driver):
    """Scroll to and highlight specific elements on the page."""
    try:
        last_save_msg = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='lastSaveTimeMsg']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", last_save_msg)
        highlight_element(driver, last_save_msg)
        logging.info("Scrolled to and highlighted 'lastSaveTimeMsg'.")
    except Exception as e:
        logging.error(f"Could not find element with id 'lastSaveTimeMsg': {e}")

    try:
        sys_msg_ul = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='2556:_sysMsgUl']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", sys_msg_ul)
        highlight_element(driver, sys_msg_ul)
        logging.info("Scrolled to and highlighted '2556:_sysMsgUl'.")
    except Exception as e:
        logging.error(f"Could not find element with id '2556:_sysMsgUl': {e}")

def main():
    """Main function to automate SAP job portal actions."""
    driver = initialize_webdriver()

    try:
        sign_in(driver)
        click_save_button(driver)
        # Wait for the save operation to complete
        time.sleep(50)

        # Scroll to the top of the page
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        scroll_and_highlight_elements(driver)
        
        # Optional: Set a larger window size to capture more of the page
        driver.set_window_size(1920, 4000)
        time.sleep(2)

        # Capture the final screenshot after all elements are in view
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        logging.info(f"Final screenshot saved at {screenshot_path}")

        # Send the screenshot via email
        send_email(screenshot_path)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        driver.save_screenshot("error_screenshot.png")
        logging.info("Error screenshot saved as 'error_screenshot.png'")
        # Save page source for debugging
        page_source_path = "error_page_source.html"
        with open(page_source_path, "w") as f:
            f.write(driver.page_source)
        logging.info(f"Page source saved at {page_source_path}")
        logging.error(f"Error occurred at URL: {driver.current_url}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
