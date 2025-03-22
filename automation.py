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
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# EMAIL SETTINGS
SENDER_EMAIL = "Mshtag1990@gmail.com"
RECEIVER_EMAIL = "Asimalsarhani@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Use environment variable for security
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# SAP LOGIN CREDENTIALS
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Setup Chrome Options
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Setup Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def automate_process():
    start_time = time.time()
    try:
        print("Opening SAP SuccessFactors...")
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true")
        time.sleep(5)

        print("Logging in...")
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)

        sign_in_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
        )
        sign_in_button.click()
        time.sleep(5)

        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Locate the Save button
        save_button_xpath = "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[1]/div[23]/div/span"
        save_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, save_button_xpath))
        )

        # Ensure it's visible
        driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
        time.sleep(2)

        # Screenshot before clicking Save
        before_click_path = "before_click.png"
        driver.save_screenshot(before_click_path)

        # Click the Save button (Double Click)
        print("Clicking Save button...")
        try:
            ActionChains(driver).move_to_element(save_button).double_click().perform()
        except:
            driver.execute_script("arguments[0].click();", save_button)

        # Wait for 50 seconds
        print("Waiting for 50 seconds to allow processing...")
        time.sleep(50)

        # Scroll back up to the top of the page
        print("Scrolling back to the top...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Click on a blank space at the top of the page
        try:
            top_element = driver.find_element(By.XPATH, "/html/body")
            top_element.click()
        except:
            print("Could not find a specific blank space, clicking on body instead.")

        # Screenshot after scrolling up
        after_click_path = "after_click.png"
        driver.save_screenshot(after_click_path)

        # Send Email with screenshots
        send_email_with_attachments([before_click_path, after_click_path])

        print(f"Process completed in {time.time() - start_time:.2f} seconds.")

    except Exception as e:
        print(f"Error during automation: {e}")

    finally:
        driver.quit()

def send_email_with_attachments(file_paths):
    try:
        print("Preparing email with screenshots...")
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        message["Subject"] = "SAP Automation Proof - Screenshots Attached"
        body = "Hello,\n\nPlease find attached the screenshots showing the automation process.\n\nBest Regards."
        message.attach(MIMEText(body, "plain"))

        for file_path in file_paths:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())

        print("Email sent successfully with screenshots.")

    except Exception as e:
        print(f"Email Error: {e}")

# Run the automation process
if __name__ == "__main__":
    automate_proc
