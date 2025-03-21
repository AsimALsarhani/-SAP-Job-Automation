import time
import os
import schedule
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 🔹 EMAIL SETTINGS (Use App Password instead of real password)
SENDER_EMAIL = "Mshtag1990@gmail.com"
RECEIVER_EMAIL = "Asimalsarhani@gmail.com"
EMAIL_PASSWORD = "IronMan@1990"  # Replace with your Gmail App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# 🔹 SAP LOGIN CREDENTIALS (Stored in Environment Variables for Security)
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# 🔹 Setup Chrome Options (Headless Mode)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 🔹 Setup Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def automate_process():
    try:
        print("🌍 Opening SAP SuccessFactors...")
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true")
        time.sleep(5)

        # 🔹 Enter Username & Password
        print("🔐 Logging in...")
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)

        # 🔹 Click "Sign In"
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
        )
        sign_in_button.click()

        # 🔹 Wait & Click "Save"
        print("💾 Clicking 'Save' button...")
        save_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Save')]"))
        )
        save_button.click()

        time.sleep(5)  # Wait for saving to complete

        # 🔹 Take Screenshot as Proof
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print("📸 Screenshot taken!")

        # 🔹 Send Email with Screenshot
        send_email_with_attachment(screenshot_path)

        # 🔹 Refresh Page
        driver.refresh()
        time.sleep(3)

    except Exception as e:
        print(f"❌ Error: {e}")

def send_email_with_attachment(file_path):
    try:
        print("📧 Sending email with screenshot...")

        # Create Email Message
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        message["Subject"] = "SAP Automation Proof - Screenshot Attached"
        body = "Hello,\n\nPlease find attached the screenshot as proof that the automation ran successfully.\n\nBest Regards,\nYour Automation Script"
        message.attach(MIMEText(body, "plain"))

        # Attach Screenshot
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={file_path}")
            message.attach(part)

        # Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())

        print("✅ Email sent successfully!")

    except Exception as e:
        print(f"❌ Email Error: {e}")

# 🔹 Schedule the Script to Run Every Hour (24 Times a Day)
schedule.every().hour.do(automate_process)

print("⏳ Automation running every hour... Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every 60 seconds
