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
from webdriver_manager.chrome import ChromeDriverManager

# Retrieve credentials from environment variables (or use defaults for testing)
SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
RECIPIENT_EMAIL = "asimalsarhani@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(screenshot_path):
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

def main():
    # Set up Chrome options and initialize the WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Step 1: Navigate to the SAP portal sign-in page
        SAP_SIGNIN_URL = ("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&"
                           "company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg")
        driver.get(SAP_SIGNIN_URL)
        print("SAP sign-in page loaded successfully.")
        
        # Allow the page to load
        time.sleep(5)

        # Step 2: Perform sign in (update the selectors as needed)
        try:
            # Example selectors – update these to match the actual page
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            username_field.send_keys(SAP_USERNAME)
            password_field.send_keys(SAP_PASSWORD)
            
            # Click on the Sign In button (update the XPath or selector accordingly)
            sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            sign_in_button.click()
            print("Sign in button clicked.")
        except Exception as e:
            print("Sign in step encountered an error or might not be required:", e)

        # Wait for sign in to complete and for the next page to load
        time.sleep(10)

        # Step 3: Scroll to the bottom and click the "Save" button
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Allow any lazy-loaded elements to appear
            save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
            save_button.click()
            print("Save button clicked.")
        except Exception as e:
            print("Save button not found or error occurred:", e)

        # Step 4: Wait for 50 seconds
        time.sleep(50)

        # Step 5: Scroll back up and click on a blank area
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
        print("Clicked on a blank area.")

        # Wait 10 seconds before taking the screenshot
        time.sleep(10)

        # Step 6: Take a screenshot and save it
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at {screenshot_path}")

        # Step 7: Send the screenshot via email
        send_email(screenshot_path)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()
