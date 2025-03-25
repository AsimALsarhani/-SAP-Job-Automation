1| import os
2| import logging
3| from logging.handlers import RotatingFileHandler
4| from email.mime.text import MIMEText
5| from email.mime.multipart import MIMEMultipart
6| from email.mime.image import MIMEImage
7| from selenium import webdriver
8| from selenium.webdriver.chrome.service import Service
9| from selenium.webdriver.chrome.options import Options
10| from selenium.webdriver.common.by import By
11| from selenium.webdriver.support.ui import WebDriverWait
12| from selenium.webdriver.support import expected_conditions as EC
13| from webdriver_manager.chrome import ChromeDriverManager
14| import tempfile
15| import smtplib
16| 
17| # Configure logging with rotation
18| log_handler = RotatingFileHandler(
19|     "selenium_debug.log", maxBytes=5 * 1024 * 1024, backupCount=5
20| )
21| logging.basicConfig(handlers=[log_handler], level=logging.ERROR)
22| 
23| # Retrieve credentials from environment variables
24| SAP_USERNAME = os.environ.get("SAP_USERNAME", "your-username")
25| SAP_PASSWORD = os.environ.get("SAP_PASSWORD", "your-password")
26| SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "mshtag1990@gmail.com")
27| SENDER_PASSWORD = os.environ.get("EMAIL_PASSWORD", "cnfz gnxd icab odza")
28| RECIPIENT_EMAIL = "asimalsarhani@gmail.com"
29| SMTP_SERVER = "smtp.gmail.com"
30| SMTP_PORT = 587
31| 
32| def send_email(screenshot_path):
33|     """Send an email with the screenshot attachment."""
34|     msg = MIMEMultipart()
35|     msg["From"] = SENDER_EMAIL
36|     msg["To"] = RECIPIENT_EMAIL
37|     msg["Subject"] = "SAP Job Portal Screenshot"
38| 
39|     body = MIMEText(
40|         "Please find attached the screenshot from the SAP job portal automation.",
41|         "plain"
42|     )
43|     msg.attach(body)
44| 
45|     with open(screenshot_path, "rb") as img_file:
46|         img = MIMEImage(img_file.read())
47|         img.add_header(
48|             "Content-Disposition",
49|             "attachment",
50|             filename=os.path.basename(screenshot_path)
51|         )
52|         msg.attach(img)
53| 
54|     try:
55|         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
56|         server.starttls()  # Secure the connection
57|         server.login(SENDER_EMAIL, SENDER_PASSWORD)
58|         server.sendmail(
59|             SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string()
60|         )
61|         server.quit()
62|         logging.info(f"Email sent to {RECIPIENT_EMAIL}")
63|     except Exception as e:
64|         logging.error(f"Error sending email: {e}")
65| 
66| def highlight_element(driver, element):
67|     """Highlights a Selenium WebElement by changing its border color via JS."""
68|     driver.execute_script(
69|         "arguments[0].style.border='3px solid red'", element
70|     )
71| 
72| def initialize_webdriver():
73|     """Initialize the Chrome WebDriver with options."""
74|     options = Options()
75|     options.add_argument("--no-sandbox")
76|     options.add_argument("--disable-dev-shm-usage")
77|     options.add_argument("--remote-debugging-port=9222")
78| 
79|     # Use a unique user-data directory
80|     unique_dir = tempfile.mkdtemp()
81|     options.add_argument(f"--user-data-dir={unique_dir}")
82| 
83|     # Temporarily remove headless mode for debugging
84|     # options.add_argument("--headless")
85| 
86|     # Initialize WebDriver without specifying version
87|     return webdriver.Chrome(
88|         service=Service(ChromeDriverManager().install()),
89|         options=options
90|     )
91| 
92| def sign_in(driver):
93|     """Sign in to the SAP portal."""
94|     SAP_SIGNIN_URL = (
95|         f"https://{SAP_USERNAME}:{SAP_PASSWORD}"
96|         "@career23.sapsf.com/career?career_company=saudiara05"
97|         "&lang=en_US&company=saudiara05"
98|     )
99|     driver.get(SAP_SIGNIN_URL)
100|     logging.info("Navigating to SAP sign-in page...")
101| 
102|     # Wait for the login fields to be present
103|     WebDriverWait(driver, 60).until(
104|         EC.presence_of_element_located((By.NAME, "username"))
105|     )
106|     logging.info("Login fields detected on the page.")
107| 
108|     # Perform sign in
109|     username_field = driver.find_element(By.NAME, "username")
110|     password_field = driver.find_element(By.NAME, "password")
111|     username_field.send_keys(SAP_USERNAME)
112|     password_field.send_keys(SAP_PASSWORD)
113|     sign_in_button = driver.find_element(
114|         By.XPATH, "//button[@data-testid='signInButton']"
115|     )
116|     sign_in_button.click()
117|     logging.info("Sign in button clicked.")
118| 
119|     # Wait for the URL to change after sign in
120|     WebDriverWait(driver, 60).until(EC.url_changes(SAP_SIGNIN_URL))
121|     logging.info(
122|         "Sign in appears successful, URL changed to %s",
123|         driver.current_url
124|     )
125|     driver.save_screenshot("login_success.png")
126| 
127| def click_save_button(driver):
128|     """Click the save button and handle potential errors."""
129|     try:
130|         save_button = WebDriverWait(driver, 20).until(
131|             EC.element_to_be_clickable(
132|                 (By.XPATH, "//button[@data-testid='saveButton']")
133|             )
134|         )
135|         save_button.click()
136|         logging.info("Save button clicked.")
137|         driver.save_screenshot("save_clicked.png")
138|     except Exception as e:
139|         logging.error(f"Save button not found or not clickable: {e}")
140| 
141| def scroll_and_highlight_elements(driver):
142|     """Scroll to and highlight specific elements on the page."""
143|     try:
144|         last_save_msg = WebDriverWait(driver, 30).until(
145|             EC.visibility_of_element_located(
146|                 (By.XPATH, "//*[@id='lastSaveTimeMsg']")
147|             )
148|         )
149|         driver.execute_script(
150|             "arguments[0].scrollIntoView(true);", last_save_msg
151|         )
152|         highlight_element(driver, last_save_msg)
153|         logging.info(
154|             "Scrolled to and highlighted 'lastSaveTimeMsg'."
155|         )
156|     except Exception as e:
157|         logging.error(
158|             f"Could not find element with id 'lastSaveTimeMsg': {e}"
159|         )
160| 
161|     try:
162|         sys_msg_ul = WebDriverWait(driver, 30).until(
163|             EC.visibility_of_element_located(
164|                 (By.XPATH, "//*[@id='2556:_sysMsgUl']")
165|             )
166|         )
167|         driver.execute_script(
168|             "arguments[0].scrollIntoView(true);", sys_msg_ul
169|         )
170|         highlight_element(driver, sys_msg_ul)
171|         logging.info(
172|             "Scrolled to and highlighted '2556:_sysMsgUl'."
173|         )
174|     except Exception as e:
175|         logging.error(
176|             f"Could not find element: {e}"
177|         )
178| 
179| def main():
180|     driver = initialize_webdriver()
181|     try:
182|         sign_in(driver)
183|         click_save_button(driver)
184|         scroll_and_highlight_elements(driver)
185|     finally:
186|         driver.quit()
187| 
188| if __name__ == "__main__":
189|     main()
