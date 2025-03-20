import os
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Replace these with actual email credentials (for testing only)
sender_email = "Mshtag1990@gmail.com"
receiver_email = "Asimalsarhani@gmail.com"
email_login = "Mshtag1990@gmail.com"
email_password = "IronMan@1990"  # ⚠️ REMOVE AFTER TESTING
smtp_server = "smtp.gmail.com"
smtp_port = 465

# ✅ Setup Chrome WebDriver (Headless Mode)
options = Options()
options.add_argument("--headless")  
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-data-dir=/tmp/chrome-data")  

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # ✅ Open SAP SuccessFactors Login Page
    driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true")
    time.sleep(5)  

    # ✅ Enter Credentials (Stored Securely as Environment Variables)
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")
    username_field.send_keys(os.getenv("SAP_USERNAME"))
    password_field.send_keys(os.getenv("SAP_PASSWORD"))

    # ✅ Click Sign In
    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
    )
    sign_in_button.click()

    # ✅ Click Save Button
    save_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Save')]"))
    )
    save_button.click()
    time.sleep(5)  

    # ✅ Take Screenshot After Save
    screenshot_path = "screenshot.png"
    driver.save_screenshot(screenshot_path)

    print("📸 Screenshot captured successfully!")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    driver.quit()

# ✅ Send Email with Screenshot Attachment
def send_email_with_attachment():
    try:
        # Create email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "📌 Automation Task Completed - Screenshot Attached"

        # Email body
        body = "Hello,\n\nThe automation task has been completed successfully. See the attached screenshot for proof.\n\nBest Regards."
        message.attach(MIMEText(body, "plain"))

        # Attach Screenshot
        with open(screenshot_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(screenshot_path)}")
            message.attach(part)

        # Connect to SMTP Server
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(email_login, email_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        print("✅ Email sent successfully with screenshot!")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Send email
send_email_with_attachment()
