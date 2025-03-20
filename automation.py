from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import smtplib, ssl
from email.message import EmailMessage
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def send_email_with_attachment(sender_email, receiver_email, subject, body, attachment_path,
                               smtp_server, smtp_port, login, password):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(body)
    
    # Read and attach the screenshot file
    with open(attachment_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)
    msg.add_attachment(file_data, maintype="image", subtype="png", filename=file_name)
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(login, password)
        server.send_message(msg)

def main():
    # Load SAP credentials (update or set these as environment variables)
    SAP_USERNAME = os.getenv("SAP_USERNAME", "your_sap_username")
    SAP_PASSWORD = os.getenv("SAP_PASSWORD", "your_sap_password")
    
    # Email settings (update these or set them as environment variables)
    sender_email = os.getenv("SENDER_EMAIL", "your_email@example.com")
    receiver_email = os.getenv("RECEIVER_EMAIL", "recipient@example.com")
    email_login = os.getenv("EMAIL_LOGIN", "your_email@example.com")
    email_password = os.getenv("EMAIL_PASSWORD", "your_email_password")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")  # e.g., smtp.gmail.com
    smtp_port = int(os.getenv("SMTP_PORT", 465))  # SSL port
    
    # Setup Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-data-dir=/tmp/chrome-data")  # Temporary user data directory
    
    # Setup Chrome WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Open the SAP SuccessFactors login page
        driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true")
        time.sleep(5)  # Wait for the page to load
        
        # Enter username and password
        username_field = driver.find_element(By.ID, "username")  # Adjust if needed
        password_field = driver.find_element(By.ID, "password")  # Adjust if needed
        username_field.send_keys(SAP_USERNAME)
        password_field.send_keys(SAP_PASSWORD)
        
        # Click the "Sign In" button using XPath
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
        )
        sign_in_button.click()
        
        # Wait for navigation and then wait for the Save element (a <span> element)
        wait = WebDriverWait(driver, 10)
        save_button = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Save')]")))
        
        # Click the Save button (if you need to perform a click action)
        save_button.click()
        
        # Wait for the action to complete
        time.sleep(2)
        
        # Capture a screenshot as proof
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        
        # Email details
        subject = "Automation Screenshot - Save Clicked"
        body = "Here is the screenshot proof after clicking Save."
        
        # Send the screenshot by email
        send_email_with_attachment(sender_email, receiver_email, subject, body,
                                   screenshot_path, smtp_server, smtp_port, email_login, email_password)
        
        # Optional: Wait for a few seconds before ending
        time.sleep(2)
    
    finally:
        driver.quit()
    
    print("Automation Completed Successfully.")

if __name__ == "__main__":
    main()
