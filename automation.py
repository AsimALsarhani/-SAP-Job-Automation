import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO)

# Retrieve credentials from environment variables
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Email password for sending email
SAP_USERNAME = os.getenv("SAP_USERNAME")  # SAP login username
SAP_PASSWORD = os.getenv("SAP_PASSWORD")  # SAP login password
FROM_EMAIL = "mshtag1990@gmail.com"  # Sender's email (from Gmail)
TO_EMAIL = "asimalsarhani@gmail.com"  # Recipient email

# Configure WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run headless for background operation
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--remote-debugging-port=9222")

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def main():
    try:
        # Step 1: Navigate to SAP SuccessFactors login page
        logging.info("Navigating to SAP SuccessFactors login page...")
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=#skipContent")

        # Step 2: Log in to SAP SuccessFactors
        logging.info("Logging in to SAP SuccessFactors...")
        username_field = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")

        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)

        login_button = driver.find_element(By.ID, "loginButton")
        login_button.click()

        # Wait for the page to load completely
        time.sleep(50)

        # Step 3: Scroll to the bottom of the page and click "Save" button
        logging.info("Scrolling to the bottom of the page and clicking 'Save' button...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        save_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Save')]"))
        )
        save_button.click()

        # Wait for the save action to complete
        time.sleep(55)

        # Step 4: Scroll to the top and click on a blank area
        logging.info("Scrolling to the top of the page and clicking on a blank area...")
        driver.execute_script("window.scrollTo(0, 0);")
        driver.find_element(By.TAG_NAME, 'body').click()

        # Wait for 10 seconds before taking a screenshot
        time.sleep(10)

        # Step 5: Take a screenshot
        screenshot_path = "screenshot.png"
        logging.info(f"Taking screenshot and saving it to {screenshot_path}...")
        driver.save_screenshot(screenshot_path)

        # Step 6: Email the screenshot
        logging.info("Sending the screenshot via email...")
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = "SAP SuccessFactors Screenshot"

        # Attach the image
        with open(screenshot_path, 'rb') as f:
            img = MIMEImage(f.read())
            msg.attach(img)

        # Setup the SMTP server and send email
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(FROM_EMAIL, EMAIL_PASSWORD)
                server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
            logging.info("Email sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")

    except Exception as e:
        logging.error(f"An error occurred during the process: {str(e)}")

    finally:
        # Close the WebDriver
        driver.quit()

if __name__ == "__main__":
    main()
