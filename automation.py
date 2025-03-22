import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """Set up the Chrome WebDriver with necessary options."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')  # Add this line for better compatibility

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_to_sap(driver):
    """Log in to the SAP career portal."""
    sap_url = 'https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg='
    driver.get(sap_url)
    try:
        username_field = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        password_field = driver.find_element(By.ID, 'password')
        login_button = driver.find_element(By.ID, 'loginButton')
        
        username_field.send_keys(os.getenv('SAP_USERNAME'))
        password_field.send_keys(os.getenv('SAP_PASSWORD'))
        login_button.click()
        
        logging.info('Login successful.')
    except Exception as e:
        logging.error(f'Login failed: {e}')
        driver.quit()
        raise

def apply_for_jobs(driver):
    """Automate the job application process."""
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'job-listing'))  # Adjust selector as needed
        )
        jobs = driver.find_elements(By.CLASS_NAME, 'job-listing')  # Adjust selector
        for job in jobs:
            try:
                job_title = job.find_element(By.CLASS_NAME, 'job-title').text
                apply_button = job.find_element(By.CLASS_NAME, 'apply-button')
                apply_button.click()
                logging.info(f'Applied for job: {job_title}')
            except Exception as e:
                logging.warning(f'Skipped a job due to error: {e}')
    except Exception as e:
        logging.error(f'Failed to apply for jobs: {e}')

def main():
    logging.basicConfig(level=logging.INFO)
    driver = setup_driver()
    try:
        login_to_sap(driver)
        apply_for_jobs(driver)
    finally:
        driver.quit()
        logging.info('WebDriver session closed.')

if __name__ == '__main__':
    main()
