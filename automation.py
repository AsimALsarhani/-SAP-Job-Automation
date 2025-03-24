from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to send an email with an attachment
def send_email(screenshot):
    from email.mime.base import MIMEBase
    from email import encoders

    # Email details
    sender_email = "mshtag1990@gmail.com"
    receiver_email = "asimalsarhani@gmail.com"
    subject = "SAP SuccessFactors Screenshot"
    body = "Please find the attached screenshot."

    # Create email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach the screenshot
    img_data = screenshot
    image = MIMEImage(img_data)
    msg.attach(image)

    try:
        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, "your_email_password")  # Replace with your email password or app password
            server.sendmail(sender_email, receiver_email, msg.as_string())
            logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# Initialize the WebDriver
driver = webdriver.Chrome()

try:
    # Navigate to SAP SuccessFactors login page
    logging.info("Navigating to SAP SuccessFactors...")
    driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=#skipContent")

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#login_field")))

    # Step 1: Wait for 50 seconds
    logging.info("Waiting for 50 seconds...")
    time.sleep(50)

    # Step 2: Scroll to the bottom and click "Save" button
    logging.info("Scrolling to the bottom and clicking Save button...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for the page to load after scroll
    save_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']"))
    )
    save_button.click()

    # Step 3: Wait for 55 seconds
    logging.info("Waiting for 55 seconds...")
    time.sleep(55)

    # Step 4: Scroll to the top and click on a blank area
    logging.info("Scrolling to the top and clicking a blank area...")
    driver.execute_script("window.scrollTo(0, 0);")
    blank_area = driver.find_element(By.XPATH, "//div[@class='some_class']")  # Update with correct class or element
    blank_area.click()

    # Step 5: Wait for 10 seconds
    logging.info("Waiting for 10 seconds...")
    time.sleep(10)

    # Step 6: Take a screenshot
    logging.info("Taking a screenshot...")
    screenshot = driver.get_screenshot_as_png()

    # Step 7: Send the screenshot via email
    send_email(screenshot)

except Exception as e:
    logging.error(f"An error occurred: {str(e)}")

finally:
    driver.quit()
    logging.info("Browser closed.")
