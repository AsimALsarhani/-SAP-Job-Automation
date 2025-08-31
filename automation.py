import os
import sys
import time
import pathlib
import traceback
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =========================
# Environment Configuration
# =========================
SAP_URL         = os.getenv("SAP_URL", "").strip()               # REQUIRED
SAP_USERNAME    = os.getenv("SAP_USERNAME", "").strip()          # REQUIRED
SAP_PASSWORD    = os.getenv("SAP_PASSWORD", "").strip()          # REQUIRED

# Optional email summary (only used if ALL are provided)
SENDER_EMAIL    = os.getenv("SENDER_EMAIL", "mshtag1990@gmail.com").strip()
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD", "cnfz gnxd icab odza").strip()        # app password or SMTP password
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "asimalsarhani@gmail.com").strip()
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "").strip()       # e.g., smtp.office365.com
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))

# Optional: Profile URL from recorded steps (not used unless you call it)
PROFILE_URL     = os.getenv("PROFILE_URL", "").strip()


# ========= Helpers / Artifacts =========
ARTIFACTS   = pathlib.Path("artifacts")
SCREENSHOTS = pathlib.Path("screenshots")
LOGS        = pathlib.Path("logs")
for p in (ARTIFACTS, SCREENSHOTS, LOGS):
    p.mkdir(parents=True, exist_ok=True)


def dump_artifacts(driver, tag: str):
    """Save the current URL, page HTML, and a screenshot."""
    try:
        (ARTIFACTS / f"{tag}.url.txt").write_text(driver.current_url, encoding="utf-8")
    except Exception:
        pass
    try:
        (ARTIFACTS / f"{tag}.html").write_text(driver.page_source, encoding="utf-8")
    except Exception:
        pass
    try:
        driver.save_screenshot(str(SCREENSHOTS / f"{tag}.png"))
    except Exception:
        pass


def assert_not_auth_error(driver):
    """Detect classic SAP 'not authorized' pages and fail early with evidence."""
    page = driver.page_source.lower()
    patterns = [
        "you are not authorized",
        "requested operation is not available",
        "not authorized to access",
    ]
    if any(s in page for s in patterns):
        dump_artifacts(driver, "auth-error")
        raise SystemExit("SAP authorization error detected (see artifacts/auth-error.html)")


def first_present(driver, selectors: List[tuple], timeout=15) -> Optional[tuple]:
    """Try a list of (By.*, selector) and return the first (element, (By, sel)) found."""
    wait = WebDriverWait(driver, timeout)
    for b, sel in selectors:
        try:
            el = wait.until(EC.presence_of_element_located((b, sel)))
            return el, (b, sel)
        except Exception:
            continue
    return None


def safe_click(driver, by, sel, timeout=15):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, sel)))
    el.click()
    time.sleep(0.5)


def safe_type(driver, by, sel, text, clear=True, timeout=15):
    el = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, sel)))
    if clear:
        try:
            el.clear()
        except Exception:
            pass
    el.send_keys(text)
    time.sleep(0.2)


def make_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opts)


# ==============================
# Login & Main Flow (customize)
# ==============================
def login_to_sap(driver):
    """Generic SAP login. Customize selectors to your landscape if needed."""
    if not (SAP_URL and SAP_USERNAME and SAP_PASSWORD):
        raise SystemExit("Missing SAP_URL/SAP_USERNAME/SAP_PASSWORD env vars")

    driver.get(SAP_URL)
    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
    dump_artifacts(driver, "01_loaded_login")
    assert_not_auth_error(driver)

    # Common username/password selectors
    user_selectors = [
        (By.ID, "sap-user"),
        (By.NAME, "sap-user"),
        (By.CSS_SELECTOR, "input[name='j_username']"),
        (By.ID, "USERNAME_FIELD"),
        (By.CSS_SELECTOR, "input[type='text']"),
    ]
    pass_selectors = [
        (By.ID, "sap-password"),
        (By.NAME, "sap-password"),
        (By.CSS_SELECTOR, "input[name='j_password']"),
        (By.ID, "PASSWORD_FIELD"),
        (By.CSS_SELECTOR, "input[type='password']"),
    ]
    login_btn_selectors = [
        (By.ID, "LOGON_BUTTON"),
        (By.ID, "sap-login-submit"),
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.XPATH, "//button[contains(., 'Logon') or contains(., 'Login')]"),
        (By.XPATH, "//input[@type='submit' or @value='Logon' or @value='Login']"),
    ]

    found_user = first_present(driver, user_selectors, timeout=20)
    found_pass = first_present(driver, pass_selectors, timeout=20)
    if not (found_user and found_pass):
        dump_artifacts(driver, "02_login_fields_not_found")
        raise SystemExit("Could not find username/password fields. Adjust selectors in automation.py")

    user_el, _ = found_user
    pass_el, _ = found_pass

    user_el.clear(); user_el.send_keys(SAP_USERNAME)
    pass_el.clear(); pass_el.send_keys(SAP_PASSWORD)

    # Try click login; otherwise submit
    btn = first_present(driver, login_btn_selectors, timeout=5)
    if btn:
        el, _ = btn
        el.click()
    else:
        pass_el.submit()

    # Wait for post-login
    time.sleep(3)
    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
    dump_artifacts(driver, "03_after_login")
    assert_not_auth_error(driver)


def perform_task(driver):
    """
    Placeholder for your real SAP steps (click tiles, run t-codes, etc.).
    Update CSS/XPath selectors to match your UI.
    """
    dump_artifacts(driver, "04_before_action")
    assert_not_auth_error(driver)

    # TODO: your real actions here.
    # Example (Fiori tile by title):
    # tile = WebDriverWait(driver, 15).until(
    #     EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'sapUshellTile')]//span[text()='My App Title']"))
    # )
    # tile.click()
    # time.sleep(2)
    # dump_artifacts(driver, "05_after_open_tile")
    # assert_not_auth_error(driver)

    time.sleep(1)
    dump_artifacts(driver, "06_after_action")
    assert_not_auth_error(driver)


def maybe_send_email(subject: str, body: str):
    """
    Optional: send a short email summary if SMTP creds are provided.
    Requires: SENDER_EMAIL, EMAIL_PASSWORD, RECIPIENT_EMAIL, EMAIL_SMTP_HOST.
    """
    if not (SENDER_EMAIL and EMAIL_PASSWORD and RECIPIENT_EMAIL and EMAIL_SMTP_HOST):
        return
    try:
        import smtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=30) as s:
            s.starttls()
            s.login(SENDER_EMAIL, EMAIL_PASSWORD)
            s.send_message(msg)
    except Exception:
        (LOGS / "email_error.log").write_text(traceback.format_exc(), encoding="utf-8")


def main():
    start_ts = time.strftime("%Y-%m-%d %H:%M:%S")
    ok = False
    err_text = ""

    driver = make_driver()
    try:
        login_to_sap(driver)
        perform_task(driver)
        ok = True
    except SystemExit as e:
        err_text = str(e)
        traceback.print_exc()
    except Exception:
        err_text = traceback.format_exc()
        dump_artifacts(driver, "99_exception")
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    end_ts = time.strftime("%Y-%m-%d %H:%M:%S")

    if ok:
        maybe_send_email(
            subject="SAP Automation: SUCCESS",
            body=f"Run window: {start_ts} → {end_ts}\nURL: {SAP_URL}\nStatus: Success"
        )
        print("SAP automation finished successfully.")
        sys.exit(0)
    else:
        maybe_send_email(
            subject="SAP Automation: FAILED",
            body=(f"Run window: {start_ts} → {end_ts}\nURL: {SAP_URL}\n"
                  f"Status: FAILED\n\nError:\n{err_text}\n\n"
                  f"Artifacts: see run artifacts (HTML/URL/screenshot).")
        )
        print("SAP automation failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
