import time
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Email credentials and recipient details
SENDER_EMAIL = "mshtag1990@gmail.com"        # Sender's email address
SENDER_PASSWORD = "cnfz gnxd icab odza"        # Replace with your email password or app-specific password
RECIPIENT_EMAIL = "asimalsarhani@gmail.com"    # Recipient's email address
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

# Set up Chrome options and initialize WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")              # Run in headless mode (no GUI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # Step 1: Navigate to the SAP portal
    SAP_URL = "https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=#skipContent"
    driver.get(SAP_URL)
    print("Page loaded successfully.")

    # Optional: Sign in if required
    # Uncomment and update the following lines with the correct locators and credentials if your page requires signing in.
    #
    # time.sleep(5)  # Wait for the login page to load
    # username_field = driver.find_element(By.ID, "username")  # Adjust locator as needed
    # password_field = driver.find_element(By.ID, "password")  # Adjust locator as needed
    # username_field.send_keys("your-username")
    # password_field.send_keys("your-password")
    # sign_in_button = driver.find_element(By.ID, "login-button")  # Adjust locator as needed
    # sign_in_button.click()
    # time.sleep(5)  # Wait for navigation after sign in

    # Wait for 50 seconds after page load (as required)
    time.sleep(50)

    # Step 2: Scroll to the bottom of the page and click the "Save" button
    try:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Allow any lazy-loaded elements to appear
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_button.click()
        print("Save button clicked.")
    except Exception as e:
        print(f"Save button not found or error occurred: {e}")

    # Wait for 55 seconds after clicking "Save"
    time.sleep(55)

    # Step 3: Scroll to the top of the page and click on a blank area
    driver.execute_script("window.scrollTo(0, 0);")
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()  # Simulate clicking on a blank area
    print("Clicked on a blank area.")

    # Wait 10 seconds before taking the screenshot
    time.sleep(10)

    # Step 4: Take a screenshot
    screenshot_path = "screenshot.png"  # Path to save the screenshot
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved at {screenshot_path}")

    # Step 5: Send the screenshot via email
    send_email(screenshot_path)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    print("Browser closed.")
