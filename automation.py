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
SENDER_EMAIL = "mshtag1990@gmail.com"  # Sender's email
SENDER_PASSWORD = "<your_password_here>"  # Replace with your email password or app password
RECIPIENT_EMAIL = "asimalsarhani@gmail.com"  # Recipient email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Define the function for sending the email with the screenshot
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

    # Sending the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"Email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Set up Chrome options and WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode if you're on a server or don't need the browser GUI
chrome_options.add_argument("--no-sandbox")  # For some environments (like CI/CD)
chrome_options.add_argument("--disable-dev-shm-usage")  # For CI/CD environments

# Initialize the ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # Step 1: Log in to the SAP SuccessFactors portal
    SAP_URL = "https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=#skipContent"
    driver.get(SAP_URL)
    print("Page loaded successfully.")

    # Wait for 50 seconds
    time.sleep(50)

    # Step 2: Scroll to the bottom of the page and click "Save" button
    try:
        save_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        driver.execute_script("arguments[0].scrollIntoView();", save_button)  # Scroll to the Save button
        save_button.click()
        print("Save button clicked.")
    except Exception as e:
        print(f"Save button not found or error occurred: {e}")

    # Wait for 55 seconds
    time.sleep(55)

    # Step 3: Scroll to the top of the page and click on a blank area
    driver.execute_script("window.scrollTo(0, 0);")  # Scroll to the top
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()  # Simulate clicking on a blank area
    print("Clicked on a blank area.")

    # Wait for 10 seconds before taking the screenshot
    time.sleep(10)

    # Step 4: Take a screenshot
    screenshot_path = "screenshot.png"  # Update with the actual path where you want to save the screenshot
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved at {screenshot_path}")

    # Step 5: Send the screenshot via email
    send_email(screenshot_path)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Clean up and close the browser
    driver.quit()
    print("Browser closed.")
