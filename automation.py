import os
import sys
import time
import pathlib
import traceback
import logging
from typing import Optional, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========= Config (Option 1: SAP_URL only) =========
SAP_URL      = os.getenv("SAP_URL", "").strip()        # include sap-client/lang if needed
SAP_USERNAME = os.getenv("SAP_USERNAME", "").strip()
SAP_PASSWORD = os.getenv("SAP_PASSWORD", "").strip()

# Optional email (set all to enable)
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "").strip()
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
SENDER_EMAIL    = os.getenv("SENDER_EMAIL", "").strip()
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD", "").strip()
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "").strip()

# Optional: if your corporate TLS breaks public runner trust
ALLOW_INSECURE = os.getenv("ALLOW_INSECURE_CERTS", "").lower() in {"1","true","yes","on"}

# ========= Folders & logging =========
ARTIFACTS   = pathlib.Path("artifacts");   ARTIFACTS.mkdir(parents=True, exist_ok=True)
SCREENSHOTS = pathlib.Path("screenshots"); SCREENSHOTS.mkdir(parents=True, exist_ok=True)
LOGS        = pathlib.Path("logs");        LOGS.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOGS / "run.log"), logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

def dump(tag: str, driver: Optional[webdriver.Chrome] = None):
    if driver:
        try: (ARTIFACTS / f"{tag}.url.txt").write_text(driver.current_url, encoding="utf-8")
        except: pass
        try: (ARTIFACTS / f"{tag}.html").write_text(driver.page_source, encoding="utf-8")
        except: pass
        try: driver.save_screenshot(str(SCREENSHOTS / f"{tag}.png"))
        except: pass

def assert_not_auth_error(driver, tag: str):
    page = driver.page_source.lower()
    if any(s in page for s in [
        "you are not authorized",
        "requested operation is not available",
        "not authorized to access"
    ]):
        dump(tag or "auth-error", driver)
        raise SystemExit("SAP authorization page detected (roles/catalog/service). See artifacts.")

def first_present(driver, selectors: List[tuple], timeout=20) -> Optional[tuple]:
    wait = WebDriverWait(driver, timeout)
    for by, sel in selectors:
        try:
            el = wait.until(EC.presence_of_element_located((by, sel)))
            return el, (by, sel)
        except Exception:
            continue
    return None

def make_driver():
    opts = Options()
    # Headless + deterministic viewport like your good run
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--force-device-scale-factor=1")
    # Let pages finish slow loads before timing out
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(120)
    if ALLOW_INSECURE:
        try:
            driver.execute_cdp_cmd("Security.setIgnoreCertificateErrors", {"ignore": True})
        except Exception:
            pass
    return driver

def send_email(subject: str, body: str, attachments: Optional[List[pathlib.Path]] = None):
    if not (EMAIL_SMTP_HOST and SENDER_EMAIL and EMAIL_PASSWORD and RECIPIENT_EMAIL):
        return
    try:
        import smtplib
        from email.message import EmailMessage
        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject
        msg.set_content(body)
        for p in attachments or []:
            if p.exists():
                msg.add_attachment(p.read_bytes(), maintype="image", subtype="png", filename=p.name)
        log.info("Connecting to SMTP server %s:%s...", EMAIL_SMTP_HOST, EMAIL_SMPT_PORT if 'EMAIL_SMPT_PORT' in globals() else EMAIL_SMTP_PORT)
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=30) as s:
            s.starttls()
            s.login(SENDER_EMAIL, EMAIL_PASSWORD)
            s.send_message(msg)
        log.info("Email dispatched successfully.")
    except Exception:
        (LOGS / "email_error.log").write_text(traceback.format_exc(), encoding="utf-8")
        log.warning("Email send failed (see logs/email_error.log)")

def robust_click_js(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", element)

def login_and_land(driver):
    if not (SAP_URL and SAP_USERNAME and SAP_PASSWORD):
        raise SystemExit("Missing SAP_URL/SAP_USERNAME/SAP_PASSWORD.")
    log.info("Opening login page…")
    try:
        driver.get(SAP_URL)
    except Exception:
        dump("00_get_timeout", driver)
        raise
    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
    dump("01_loaded_login", driver)
    assert_not_auth_error(driver, "01_loaded_login")

    # Some landscapes wrap fields in an iframe — try to switch; if not, continue
    log.info("Checking for login iframe…")
    try:
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        if frames:
            driver.switch_to.frame(frames[0])
            log.info("Switched into first iframe.")
    except Exception:
        log.info("No frame found, proceeding without switching.")

    # Your good-run selectors
    log.info("Waiting for username field…")
    u = WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR, "input[id*='username'],input[name='j_username'],#sap-user,[name='sap-user']"
    )))
    log.info("Waiting for password field…")
    p = WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR, "input[type='password'],input[name='j_password'],#sap-password,[name='sap-password']"
    )))
    u.clear(); u.send_keys(SAP_USERNAME)
    p.clear(); p.send_keys(SAP_PASSWORD)

    log.info("Waiting for Sign In button…")
    login_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((
        By.XPATH, "//button[contains(.,'Sign In') or contains(.,'Login') or contains(.,'Logon')] | //input[@type='submit']"
    )))
    log.info("Sign In button found. Clicking.")
    robust_click_js(driver, login_btn)

    time.sleep(2)
    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
    dump("03_after_login", driver)
    assert_not_auth_error(driver, "03_after_login")

def save_profile_and_prove(driver):
    # Scroll to bottom to force lazy content, like in your good run
    log.info("Scrolling to bottom of the page…")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.0)

    # Wait for Save button that matched your log: //*[contains(@id, ':_saveBtn')]
    save_xpath = "//*[contains(@id, ':_saveBtn')]"
    log.info("Waiting for Save button presence using selector: %s", save_xpath)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, save_xpath)))
    log.info("Save button present in DOM.")
    save_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, save_xpath)))
    log.info("Scrolling Save button into view…")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
    time.sleep(0.4)
    log.info("Waiting for Save button to be clickable after scrolling…")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, save_xpath)))
    log.info("Save button is clickable. Login assumed successful.")
    log.info("Re-locating Save button for post-login click…")
    save_btn = driver.find_element(By.XPATH, save_xpath)
    log.info("Clicking Save button using JavaScript…")
    robust_click_js(driver, save_btn)
    log.info("Save button clicked.")
    time.sleep(2.0)

    # Focus the main profile container (as your log shows)
    profile_sel = "#rcmCandidateProfileCtr"
    log.info("Waiting for the main profile container (%s)…", profile_sel)
    container = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, profile_sel)))
    log.info("Profile container found. Scrolling into view…")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", container)
    time.sleep(0.5)
    log.info("Clicking the profile container…")
    robust_click_js(driver, container)
    log.info("Profile container clicked.")

    # Zoom out to 50% to capture broader view, then screenshot
    log.info("Zooming out to capture a broader view (set zoom to 50%)…")
    driver.execute_script("document.body.style.zoom='0.5';")
    time.sleep(0.7)
    proof_path = SCREENSHOTS / "post_run_proof.png"
    driver.save_screenshot(str(proof_path))
    log.info("Final screenshot saved as %s", proof_path.name)

def main():
    start_ts = time.strftime("%Y-%m-%d %H:%M:%S")
    ok, err = False, ""
    driver = make_driver()
    try:
        log.info("Login attempt: 1/1")
        login_and_land(driver)
        save_profile_and_prove(driver)
        ok = True
    except SystemExit as e:
        err = str(e); log.error(err); traceback.print_exc()
    except Exception:
        err = traceback.format_exc(); log.error("Unhandled exception:\n%s", err); dump("99_exception", driver)
    finally:
        # Always capture a final state image
        try:
            driver.execute_script("document.body.style.zoom='0.67';")
            driver.save_screenshot(str(SCREENSHOTS / "final_state_report.png"))
        except Exception:
            pass
        try:
            driver.quit()
            log.info("Browser terminated")
        except Exception:
            pass

    # Optional email with attached proof(s)
    if ok:
        body = f"Profile save + proof completed.\nStart: {start_ts}\nEnd: {time.strftime('%Y-%m-%d %H:%M:%S')}\nURL: {SAP_URL}"
        send_email("SAP Automation: SUCCESS", body, attachments=[
            SCREENSHOTS / "post_run_proof.png",
            SCREENSHOTS / "final_state_report.png"
        ])
        sys.exit(0)
    else:
        body = f"Automation FAILED.\nStart: {start_ts}\nEnd: {time.strftime('%Y-%m-%d %H:%M:%S')}\nURL: {SAP_URL}\n\nError:\n{err}"
        send_email("SAP Automation: FAILED", body, attachments=[
            SCREENSHOTS / "post_run_proof.png",
            SCREENSHOTS / "final_state_report.png"
        ])
        sys.exit(1)

if __name__ == "__main__":
    main()
