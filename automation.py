import os
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Retrieve credentials from environment variables
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # If needed later

# ✅ Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# ✅ Use a unique temporary user data directory to prevent conflicts
temp_dir = tempfile.mkdtemp()
chrome_options.add_argument(f"--user-data-dir={temp_dir}")

# ✅ Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.maximize_window()

try:
    # ✅ Open SAP webpage
    driver.get("https://your-sap-url.com")  # Replace with the correct SAP URL

    # ✅ Log in (Using the same SAP login field IDs as before)
    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "j_username")))
    password = driver.find_element(By.ID, "j_password")
    
    username.send_keys(SAP_USERNAME)  # Use environment variable
    password.send_keys(SAP_PASSWORD)  # Use environment variable
    password.send_keys(Keys.RETURN)
    
    # ✅ Wait for page to load
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Dashboard')]")))  # Modify as needed

    # ✅ Scroll to the Save button
    save_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/as:ajaxinclude/as:ajaxinclude/div[2]/div[2]/div/form/div[3]/div[2]/div[1]/div[23]/d
