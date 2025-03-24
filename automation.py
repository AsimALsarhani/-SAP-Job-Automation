import time
import smtplib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Initialize the WebDriver
driver = webdriver.Chrome()

# Step 1: Log in to SAP SuccessFactors
driver.get("https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg=#skipContent")
time.sleep(5)  # Adjust depending on load time

# Fill in login credentials (replace with actual credentials)
username = driver.find_element(By.ID, "username")
password = driver.find_element(By.ID, "password")
username.send_keys("your_username")
password.send_keys("your_password")
password.send_keys(Keys.RETURN)

time.sleep(50)  # Wait for 50 seconds

# Step 2: Scroll to the bottom and click "Save" button
save_button = driver.find_element(By.XPATH, "//button[contains(text(),'Save')]")
driver.execute_script("arguments[0].scrollIntoView();", save_button)
save_button.click()

time.sleep(55)  # Wait for 55 seconds

# Step 3: Scroll to the top and click a blank area
driver.execute_script("window.scrollTo(0, 0);")
blank_area = driver.find_element(By.XPATH, "//body")
ActionChains(driver).move_to_element(blank_area).click().perform()

time.sleep(10)  # Wait for 10 seconds

# Step 4: Take a screenshot
screenshot_path = "screenshot.png"
driver.save_screenshot(screenshot_path)

# Close the browser
driver.quit()

# Step 5: Email the screenshot
def send_email(subject, body, to_email, screenshot_path):
    from_email = "mshtag1990@gmail.com"
    password = "your_email_password"  # Use environment variables or secure methods for password handling

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(body)

    # Attach the screenshot
    part = MIMEBase('application', 'octet-stream')
    with open(screenshot_path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={screenshot_path}')
    msg.attach(part)

    # Send the email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

# Send the email with the screenshot
send_email("SAP SuccessFactors Screenshot", "Attached is the screenshot from the SAP SuccessFactors portal.", "asimalsarhani@gmail.com", screenshot_path)
