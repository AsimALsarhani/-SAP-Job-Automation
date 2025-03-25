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
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
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
    # For debugging, consider disabling headless mode (comment out the next line)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Step 1: Navigate to the SAP portal sign-in page
        SAP_SIGNIN_URL = "https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05"
        driver.get(SAP_SIGNIN_URL)
        print("SAP sign-in page loaded successfully.")

        # Wait for the login fields to be present
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "username")))
        print("Login fields are present.")

        # Step 2: Perform sign in
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)

        sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
        sign_in_button.click()
        print("Sign in button clicked.")

        # Wait for URL change after login; then capture a debug screenshot
        WebDriverWait(driver, 30).until(EC.url_changes(SAP_SIGNIN_URL))
        print("Login successful, URL changed to:", driver.current_url)
        driver.save_screenshot("login_success.png")
        print("Login screenshot saved as 'login_success.png'.")

        # Step 3: Click the Save button and wait for changes
        try:
            save_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save')]"))
            )
            save_button.click()
            print("Save button clicked.")
            driver.save_screenshot("save_clicked.png")
            print("Save click screenshot saved as 'save_clicked.png'.")
        except Exception as e:
            print("Save button not found or not clickable:", e)

        time.sleep(50)  # Wait for the save operation to complete

        # Step 4: Scroll to the top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Now wait for and scroll to the target elements
        try:
            last_save_msg = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='lastSaveTimeMsg']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", last_save_msg)
            highlight_element(driver, last_save_msg)
            print("Scrolled to and highlighted 'lastSaveTimeMsg'.")
            time.sleep(2)
        except Exception as e:
            print("Could not find element with id 'lastSaveTimeMsg':", e)

        try:
            sys_msg_ul = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='2556:_sysMsgUl']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", sys_msg_ul)
            highlight_element(driver, sys_msg_ul)
            print("Scrolled to and highlighted '2556:_sysMsgUl'.")
            time.sleep(2)
        except Exception as e:
            print("Could not find element with id '2556:_sysMsgUl':", e)

        # Optional: Set a larger window size to capture more of the page
        driver.set_window_size(1920, 4000)
        time.sleep(2)

        # Step 5: Capture the final screenshot after all elements are in view
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Final screenshot saved at {screenshot_path}")

        # Step 6: Send the screenshot via email
        send_email(screenshot_path)

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.save_screenshot("debug_error.png")
        print("Debug error screenshot saved as 'debug_error.png'.")
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()
