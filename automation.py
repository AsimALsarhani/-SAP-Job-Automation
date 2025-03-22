import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_driver():
    """Configure and return a Chrome WebDriver with robust options."""
    options = webdriver.ChromeOptions()
    
    # Headless mode configuration
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Enable browser logging
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_to_sap(driver):
    """Handle SAP login with multiple checks and fallbacks."""
    sap_url = 'https://career23.sapsf.com/career?career_company=saudiara05&lang=en_US&company=saudiara05&site=&loginFlowRequired=true&_s.crb=7rUayllvSa7Got9Vb3iPnhO3PDDqujW7AwjljaAL6sg='
    
    try:
        driver.get(sap_url)
        logging.info(f"Loaded SAP URL: {sap_url}")

        # Wait for critical elements with multiple fallbacks
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

        # Check for login form using multiple identifiers
        login_form = WebDriverWait(driver, 30).until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, 'loginForm')),
                EC.presence_of_element_located((By.CSS_SELECTOR, 'form[role="form"]'))
            )
        )

        # Find elements with multiple locator strategies
        username_field = WebDriverWait(login_form, 15).until(
            EC.visibility_of_element_located((By.ID, 'username'))
        )
        
        password_field = WebDriverWait(login_form, 15).until(
            EC.visibility_of_element_located((By.ID, 'password'))
        )
        
        login_button = WebDriverWait(login_form, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Sign In") or @id="loginButton"]'))
        )

        # Credential handling
        username = os.getenv('SAP_USERNAME')
        password = os.getenv('SAP_PASSWORD')
        
        if not username or not password:
            raise ValueError("Missing credentials in environment variables")

        username_field.clear()
        username_field.send_keys(username)
        
        password_field.clear()
        password_field.send_keys(password)

        # Click with JavaScript as fallback
        try:
            login_button.click()
        except:
            driver.execute_script("arguments[0].click();", login_button)

        # Post-login verification
        WebDriverWait(driver, 30).until(
            EC.any_of(
                EC.url_contains('/career'),
                EC.presence_of_element_located((By.CLASS_NAME, 'job-listing'))
            )
        )
        logging.info("Successfully logged in")

    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        driver.save_screenshot('login_failure.png')
        raise

def apply_for_jobs(driver):
    """Job application logic with enhanced element handling."""
    try:
        # Wait for jobs to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.job-listing, .jobItem'))
        )

        jobs = driver.find_elements(By.CSS_SELECTOR, '.job-listing, .jobItem')
        logging.info(f"Found {len(jobs)} jobs")

        for index, job in enumerate(jobs):
            try:
                job_title = job.find_element(By.CSS_SELECTOR, '.job-title, .jobTitle').text
                company = job.find_element(By.CSS_SELECTOR, '.company-name, .employerName').text
                location = job.find_element(By.CSS_SELECTOR, '.job-location, .jobLocation').text
                
                logging.info(f"Processing job #{index+1}: {job_title} at {company} ({location})")

                apply_button = WebDriverWait(job, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.apply-button, .applyBtn'))
                )
                
                # Scroll into view before clicking
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", apply_button)
                time.sleep(1)  # Allow smooth scroll to complete
                apply_button.click()
                
                # Handle application form
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'form.application-form'))
                )
                
                # Add your application form filling logic here
                # ...
                
                logging.info(f"Successfully applied to: {job_title}")
                
                # Return to job list
                driver.back()
                time.sleep(2)

            except Exception as job_error:
                logging.warning(f"Failed to process job #{index+1}: {str(job_error)}")
                continue

    except Exception as e:
        logging.error(f"Job application process failed: {str(e)}")
        driver.save_screenshot('application_error.png')
        raise

def main():
    driver = setup_driver()
    try:
        login_to_sap(driver)
        apply_for_jobs(driver)
    except Exception as e:
        logging.error(f"Main execution failed: {str(e)}")
        # Capture browser logs for debugging
        for entry in driver.get_log('browser'):
            logging.error(f"Browser Console: {entry}")
    finally:
        driver.quit()
        logging.info("Browser session closed")

if __name__ == '__main__':
    main()
