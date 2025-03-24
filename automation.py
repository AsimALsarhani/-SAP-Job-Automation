import time
import logging
import socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# SAP Login URL
SAP_LOGIN_URL = "https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US"

# Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
logging.info("Initializing WebDriver...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to resolve DNS manually before navigating
def resolve_dns_and_navigate(url, retries=3, delay=5):
    host = url.split("//")[-1].split("/")[0]  # Extract domain from URL

    for attempt in range(retries):
        try:
            logging.info(f"Resolving DNS for {host} (Attempt {attempt+1}/{retries})...")
            ip_address = socket.gethostbyname(host)  # Resolve DNS manually
            logging.info(f"Resolved {host} to {ip_address}")

            # Navigate using the resolved IP instead of the domain
            driver.get(url)
            return True
        except Exception as e:
            logging.error(f"DNS resolution error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    
    return False  # Fail after retries

# Attempt to navigate with improved DNS handling
if not resolve_dns_and_navigate(SAP_LOGIN_URL):
    logging.error("Failed to resolve DNS after multiple retries.")
    driver.quit()
    exit(1)

# Continue with SAP login...
logging.info("Navigated successfully to SAP login page.")
