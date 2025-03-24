import time
import os
import smtplib
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

# Retrieve credentials from environment variables
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "your-app-password")
RECIPIENT_EMAIL = "asimalsarhani@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(screenshot_path):
    """Send an email with the screenshot attachment."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "SAP Job Portal Screenshot"

    body = MIMEText("Please find attached the screenshot from the SAP job portal automation.", 'plain')
    msg.attach(body)

    with open(screenshot_path, 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(screenshot_path))
        msg.attach(img)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"Email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Error sending email: {e}")

def highlight_element(driver, element):
    """Highlights a Selenium WebElement by changing its border color via JavaScript."""
    driver.execute_script("arguments[0].style.border='3px solid red'", element)

def main():
    """Main function to automate SAP job portal actions."""
    # Set up Chrome options and initialize WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Step 1: Navigate to the SAP portal sign-in page
        SAP_SIGNIN_URL = "https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05"
        driver.get(SAP_SIGNIN_URL)
        print("SAP sign-in page loaded successfully.")

        # Wait for the login fields
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username")))

        # Step 2: Perform sign in
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)

        sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
        sign_in_button.click()
        print("Sign in button clicked.")

        # Wait for the page to load after login
        WebDriverWait(driver, 15).until(EC.url_changes(SAP_SIGNIN_URL))

        # Step 3: Click the Save button and wait for changes
        try:
            save_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save')]")
            )
            save_button.click()
            print("Save button clicked.")
        except Exception as e:
            print("Save button not found or not clickable:", e)

        time.sleep(50)  # Wait for save operation to complete

        # Step 4: Ensure the target elements are visible
        try:
            # Locate and scroll to the "lastSaveTimeMsg" element
            last_save_msg = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='lastSaveTimeMsg']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", last_save_msg)
            highlight_element(driver, last_save_msg)
            print("Scrolled to and highlighted 'lastSaveTimeMsg'.")
            time.sleep(2)  # Allow UI to update

        except Exception as e:
            print("Could not find element with id 'lastSaveTimeMsg':", e)

        try:
            # Locate and scroll to the "2556:_sysMsgUl" element
            sys_msg_ul = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='2556:_sysMsgUl']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", sys_msg_ul)
            highlight_element(driver, sys_msg_ul)
            print("Scrolled to and highlighted '2556:_sysMsgUl'.")
            time.sleep(2)

        except Exception as e:
            print("Could not find element with id '2556:_sysMsgUl':", e)

        # Step 5: Capture the screenshot
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at {screenshot_path}")

        # Step 6: Send the screenshot via email
        send_email(screenshot_path)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()
