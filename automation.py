import os
import time
import logging
from logging.handlers import RotatingFileHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def setup_logging():
    log_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    log_handler = RotatingFileHandler(
        "selenium_debug.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    logging.info("Logging setup complete.")

def login_to_website(driver, url, username, password):
    driver.get(url)
    logging.info("Opened website: %s", url)
    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        logging.info("Entered login credentials and submitted form.")
        WebDriverWait(driver, 10).until(EC.url_changes(url))
        logging.info("Sign in appears successful, URL changed to %s", driver.current_url)
    except (NoSuchElementException, TimeoutException) as e:
        logging.error("Error during login: %s", e)
        driver.quit()

def find_and_scroll_to_element(driver, element_id):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        logging.info("Scrolled to and highlighted element with ID: %s", element_id)
    except (NoSuchElementException, TimeoutException) as e:
        logging.error("Could not find element with id '%s': %s", element_id, e)

def extract_text(driver, element_id):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        text = element.text
        logging.info("Extracted text from element ID '%s': %s", element_id, text)
        return text
    except (NoSuchElementException, TimeoutException) as e:
        logging.error("Failed to extract text from element ID '%s': %s", element_id, e)
        return None

def main():
    setup_logging()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for efficiency
    driver = webdriver.Chrome(options=options)
    try:
        login_to_website(
            driver, "https://example.com/login", "your_username", "your_password"
        )
        find_and_scroll_to_element(driver, "lastSaveTimeMsg")
        extracted_text = extract_text(driver, "lastSaveTimeMsg")
        if extracted_text:
            print("Extracted Text:", extracted_text)
    finally:
        driver.quit()
        logging.info("WebDriver session closed.")

if __name__ == "__main__":
    main()
