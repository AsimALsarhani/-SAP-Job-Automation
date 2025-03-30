import os
import time
import logging
import smtplib
from email.message import EmailMessage
from selenium import webdriver
from selenium.common import WebDriverException, TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

# Environment variables with defaults for local testing
SAP_USERNAME = os.environ.get("SAP_USERNAME", "default-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "default-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "asimalsarhani@gmail.com")
SAP_URL = os.environ.get("SAP_URL")  # No default - must be provided

if not SAP_URL:
    raise EnvironmentError("SAP_URL environment variable is required")

def configure_browser():
    """Configure Chrome with enterprise-grade options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Mask automation signals
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def safe_interaction(element, text=None):
    """Universal method for reliable element interaction"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        ActionChains(driver).move_to_element(element).pause(0.5).perform()
        
        if text:
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(0.1)
        return True
    except Exception as e:
        logging.error(f"Interaction failed: {str(e)}")
        return False

def perform_login(driver):
    """Enterprise SAP login with multiple fallback strategies"""
    try:
        # Username handling
        username = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#username, input[name='username']"))
        )
        if not safe_interaction(username, SAP_USERNAME):
            raise Exception("Username entry failed")

        # Password handling
        password = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#password[type='password']"))
        )
        if not safe_interaction(password, SAP_PASSWORD):
            raise Exception("Password entry failed")

        # Sign-in button detection
        signin_selectors = [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//*[contains(translate(., 'SIGN IN', 'sign in'), 'sign in')]"),
            (By.ID, "logOnFormSubmit")
        ]
        
        for selector in signin_selectors:
            try:
                btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(selector))
                driver.execute_script("arguments[0].click();", btn)
                logging.info(f"Clicked sign-in using {selector}")
                return True
            except (TimeoutException, NoSuchElementException):
                continue
                
        raise Exception("No valid sign-in button found")

    except Exception as e:
        driver.save_screenshot("login_error.png")
        logging.error(f"Login failed: {str(e)}")
        raise

def verify_dashboard(driver):
    """Comprehensive post-login verification"""
    try:
        # Check for error messages first
        WebDriverWait(driver, 10).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".error-message, .alert-danger"))
        )
        
        # Dashboard verification
        WebDriverWait(driver, 60).until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "mainDashboard")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Dashboard']")),
                EC.url_contains("dashboard")
            )
        )
        logging.info("Dashboard verification passed")
        return True
        
    except Exception as e:
        driver.save_screenshot("dashboard_error.png")
        logging.error(f"Dashboard verification failed: {str(e)}")
        raise

def main():
    driver = None
    try:
        driver = configure_browser()
        logging.info("Browser initialized successfully")

        # Load SAP URL with retries
        for attempt in range(3):
            try:
                driver.get(SAP_URL)
                WebDriverWait(driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == 'complete'
                )
                if driver.find_elements(By.CSS_SELECTOR, "input#username"):
                    logging.info("Login page loaded successfully")
                    break
            except WebDriverException as e:
                if attempt == 2:
                    raise
                logging.warning(f"Page load attempt {attempt+1} failed: {str(e)}")
                time.sleep(5)

        # Execute login sequence
        perform_login(driver)
        verify_dashboard(driver)

        # Save operation
        save_btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Save') or contains(@id, 'save')]"))
        )
        driver.execute_script("arguments[0].click();", save_btn)
        logging.info("Save action completed")

        # Capture status
        status_element = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Last update') or contains(@id, 'lastSave')]"))
        )
        driver.save_screenshot("status_screenshot.png")

        # Email notification
        msg = EmailMessage()
        msg["Subject"] = "SAP Automation Success"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg.set_content("SAP automation completed successfully")
        
        with open("status_screenshot.png", "rb") as f:
            msg.add_attachment(f.read(), maintype="image", subtype="png", filename="status.png")
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        logging.info("Notification email sent")

    except Exception as e:
        logging.error(f"Main execution failed: {str(e)}")
        if driver:
            driver.save_screenshot("final_error.png")
        raise
    finally:
        if driver:
            driver.quit()
            logging.info("Browser terminated")

if __name__ == "__main__":
    main()
