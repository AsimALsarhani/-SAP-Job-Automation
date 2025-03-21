import time
import os
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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# EMAIL SETTINGS (Use your Gmail App Password here)
SENDER_EMAIL = "Mshtag1990@gmail.com"
RECEIVER_EMAIL = "Asimalsarhani@gmail.com"
EMAIL_PASSWORD = "IronMan@1990"  # Replace with your Gmail App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# SAP LOGIN CREDENTIALS (provided via GitHub Secrets / Environment Variables)
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Setup Chrome Options (Headless Mode)
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Setup Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def automate_process():
    start_time = time.time()
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Opening SAP SuccessFactors...")
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true")
        time.sleep(5)  # Wait for the page to load

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Page loaded. Logging in...")
        # Enter Username & Password
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Clicking Sign In button...")
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
        )
        sign_in_button.click()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sign In clicked.")

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Waiting for Save button...")
        save_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Save')]"))
        )
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Save button found. Clicking Save...")
        save_button.click()
        time.sleep(5)  # Wait for saving to complete

        # Take Screenshot as Proof
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Screenshot taken.")

        # Send Email with the Screenshot Attachment
        send_email_with_attachment(screenshot_path)

        # Refresh Page (if needed)
        driver.refresh()
        time.sleep(3)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Process completed in {time.time() - start_time:.2f} seconds.")

    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error during automation: {e}")

    finally:
        driver.quit()

def send_email_with_attachment(file_path):
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Preparing email with screenshot...")
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        message["Subject"] = "SAP Automation Proof - Screenshot Attached"
        body = ("Hello,\n\n"
                "Please find attached the screenshot as proof that the SAP automation ran successfully.\n\n"
                "Best Regards,\n"
                "Your Automation Script")
        message.attach(MIMEText(body, "plain"))

        # Attach the screenshot file
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
            message.attach(part)

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Connecting to SMTP server...")
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Logging into SMTP server...")
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Email sent successfully!")

    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Email Error: {e}")

# Run the automation process once
automate_process()
