import os
import time
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging with timestamps
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Retrieve credentials from environment variables
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # For mshtag1990@gmail.com

if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
    logger.error("Missing one or more required environment variables: SAP_USERNAME, SAP_PASSWORD, or EMAIL_PASSWORD")
    raise ValueError("Missing credentials")

# SAP SuccessFactors login URL (provided)
SAP_URL = (
    "https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&"
    "company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg="
)

def setup_driver():
    """
    Set up the Chrome WebDriver using webdriver_manager.
    Use the --incognito flag to force a fresh session and avoid user-data conflicts.
    """
    chrome_options = Options()
    chrome_options.headless = True  # Change to False for debugging (visible browser)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--incognito")  # Use incognito mode for a fresh session
    # Do NOT specify a fixed user-data-dir so that Chrome uses its default temporary profile.
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login_to_sap(driver):
    """Log in to the SAP SuccessFactors portal using explicit waits and detailed logging."""
    try:
        logger.info("Navigating to SAP login page.")
        driver.get(SAP_URL)
        time.sleep(5)  # Allow the page to load
        
        logger.info("Page title: " + driver.title)
        
        # XPath for the username field (update if necessary)
        username_xpath = (
            "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/"
            "div[3]/div[2]/div[2]/div/div/div[2]/div/div/table/tbody/tr[1]/td[2]/input"
        )
        username_field = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, username_xpath))
        )
        logger.info("Username field located.")
        username_field.send_keys(SAP_USERNAME)
        logger.info("Entered SAP username.")
        
        # XPath for the password field (update if necessary)
        password_xpath = (
            "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/"
            "div[3]/div[2]/div[2]/div/div/div[2]/div/div/table/tbody/tr[2]/td[2]/div/input[1]"
        )
        password_field = WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, password_xpath))
        )
        logger.info("Password field located.")
        password_field.send_keys(SAP_PASSWORD)
        logger.info("Entered SAP password.")
        
        # XPath for the login button (update if necessary)
        login_button_xpath = "//button[@type='submit']"
        login_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        logger.info("Login button is clickable.")
        login_button.click()
        logger.info("Clicked on the login button.")
        
        # Wait for an element that confirms successful login (update this XPath as needed)
        success_xpath = "//div[@id='dashboard']"  # Example; adjust to an element that appears after login
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, success_xpath))
        )
        logger.info("Logged in successfully.")
        
    except TimeoutException as te:
        logger.error("Timeout while waiting for an element during login.")
        logger.error("Page source snippet: " + driver.page_source[:1000])
        driver.quit()
        raise te
    except NoSuchElementException as ne:
        logger.error(f"Element not found: {ne}")
        logger.error("Page source snippet: " + driver.page_source[:1000])
        driver.quit()
        raise ne
    except Exception as e:
        logger.error(f"Error during SAP login process: {e}")
        try:
            logger.error("Page source snippet: " + driver.page_source[:1000])
        except Exception:
            logger.error("Could not retrieve page source.")
        driver.quit()
        raise e

def perform_actions(driver):
    """
    Perform the following actions:
      1. Wait 50 seconds.
      2. Scroll down to the bottom and click the "Save" button.
      3. Wait 55 seconds.
      4. Scroll up to the top and click on a blank area.
      5. Wait 10 seconds.
    """
    try:
        logger.info("Waiting 50 seconds after login.")
        time.sleep(50)
        
        # Scroll down to the bottom of the page
        logger.info("Scrolling to the bottom of the page.")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Click the "Save" button (update the selector as needed)
        save_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Save')]"))
        )
        logger.info("Save button located and clickable.")
        save_button.click()
        logger.info("Clicked on the Save button.")
        
        logger.info("Waiting 55 seconds after clicking Save.")
        time.sleep(55)
        
        # Scroll back up to the top
        logger.info("Scrolling back to the top of the page.")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Click on a blank white area (using the body as a fallback)
        blank_area = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.TAG_NAME, "body"))
        )
        blank_area.click()
        logger.info("Clicked on a blank area at the top of the page.")
        
        logger.info("Waiting 10 seconds before taking a screenshot.")
        time.sleep(10)
        
    except Exception as e:
        logger.error(f"Error during post-login actions: {e}")
        driver.quit()
        raise e

def take_screenshot(driver, file_path="screenshot.png"):
    """Take a screenshot and save it to file_path."""
    try:
        driver.save_screenshot(file_path)
        logger.info(f"Screenshot saved as {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        raise e

def send_email(screenshot_path, sender_email="mshtag1990@gmail.com", receiver_email="asimalsarhani@gmail.com"):
    """
    Send an email with the screenshot attached.
    Uses Gmail's SMTP_SSL. Ensure EMAIL_PASSWORD is an app password for mshtag1990@gmail.com.
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = "SAP Automation Screenshot"
        body = "Attached is the screenshot from the SAP automation run."
        msg.attach(MIMEText(body, "plain"))
        
        with open(screenshot_path, "rb") as file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={screenshot_path}")
        msg.attach(part)
        
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, os.getenv("EMAIL_PASSWORD"))
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise e

def main():
    driver = setup_driver()
    try:
        login_to_sap(driver)
        perform_actions(driver)
        screenshot_path = take_screenshot(driver)
        send_email(screenshot_path)
    finally:
        driver.quit()
        logger.info("WebDriver closed.")

if __name__ == "__main__":
    main()
