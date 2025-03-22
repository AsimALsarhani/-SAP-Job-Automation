import logging
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        load_dotenv()
        SAP_USERNAME = os.getenv('SAP_USERNAME')
        SAP_PASSWORD = os.getenv('SAP_PASSWORD')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

        if not SAP_USERNAME or not SAP_PASSWORD or not EMAIL_PASSWORD:
            logging.error("Environment variables for SAP credentials and email password are not set.")
            return

        logging.debug(f"SAP_USERNAME: {SAP_USERNAME}")
        logging.debug("Starting WebDriver...")

        driver = webdriver.Chrome(ChromeDriverManager().install())
        logging.debug("WebDriver started successfully.")

        # Your automation logic here...

        driver.quit()
        logging.debug("WebDriver closed successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
