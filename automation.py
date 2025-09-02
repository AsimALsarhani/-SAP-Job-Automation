import os
import sys
import time
import pathlib
import traceback
from typing import Optional, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# === Config from Secrets ===
SAP_URL      = os.getenv("SAP_URL", "").strip()        # include sap-client/lang if required
SAP_USERNAME = os.getenv("SAP_USERNAME", "").strip()
SAP_PASSWORD = os.getenv("SAP_PASSWORD", "").strip()
ALLOW_INSECURE = os.getenv("ALLOW_INSECURE_CERTS", "").lower() in {"1","true","yes","on"}

ARTIFACTS   = pathlib.Path("artifacts");   ARTIFACTS.mkdir(exist_ok=True, parents=True)
SCREENSHOTS = pathlib.Path("screenshots"); SCREENSHOTS.mkdir(exist_ok=True, parents=True)
LOGS        = pathlib.Path("logs");        LOGS.mkdir(exist_ok=True, parents=True)

def dump_artifacts(driver, tag: str):
    try: (ARTIFACTS / f"{tag}.url.txt").write_text(driver.current_url, encoding="utf-8")
    except: pass
    try: (ARTIFACTS / f"{tag}.html").write_text(driver.page_source, encoding="utf-8")
    except: pass
    try: driver.save_screenshot(str(SCREENSHOTS / f"{tag}.png"))
    except: pass

def assert_not_auth_error(driver, tag: str):
    page = driver.page_source.lower()
    if any(s in page for s in ["you are not authorized","requested operation is not available","not authorized to access"]):
        dump_artifacts(driver, tag or "auth-error")
        raise SystemExit("SAP authorization error – see artifacts for URL/HTML.")

def first_present(driver, selectors: List[tuple], timeout=15) -> Optional[tuple]:
    wait = WebDriverWait(driver, timeout)
    for by, sel in selectors:
        try: return wait.until(EC.presence_of_element_located((by, sel))), (by, sel)
        except: continue
    return None

def make_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    # If TLS via corporate CA blocks navigation, allow insecure certs (toggle by secret)
    if ALLOW_INSECURE:
        opts.add_argument("--ignore-certificate-errors")
        opts.add_argument("--allow-insecure-localhost")
    driver = webdriver.Chrome(options=opts)
    if ALLOW_INSECURE:
        try:
            driver.capabilities["acceptInsecureCerts"] = True
        except Exception:
            pass
    return driver

def login_to_sap(driver):
    if not (SAP_URL and SAP_USERNAME and SAP_PASSWORD):
        raise SystemExit("Missing SAP_URL/SAP_USERNAME/SAP_PASSWORD secrets.")

    # Wrap driver.get with explicit timeout handling to capture artifacts on hang
    try:
        driver.set_page_load_timeout(120)
        driver.get(SAP_URL)
    except Exception as e:
        # Capture as much as possible even if get() timed out
        dump_artifacts(driver, "00_get_timeout")
        raise

    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState")=="complete")
    dump_artifacts(driver, "01_loaded_login")
    assert_not_auth_error(driver, "01_loaded_login")

    user_fields = [
        (By.ID,"sap-user"), (By.NAME,"sap-user"),
        (By.CSS_SELECTOR,"input[name='j_username']"),
        (By.ID,"USERNAME_FIELD"), (By.CSS_SELECTOR,"input[type='text']")
    ]
    pass_fields = [
        (By.ID,"sap-password"), (By.NAME,"sap-password"),
        (By.CSS_SELECTOR,"input[name='j_password']"),
        (By.ID,"PASSWORD_FIELD"), (By.CSS_SELECTOR,"input[type='password']")
    ]
    login_btns  = [
        (By.ID,"LOGON_BUTTON"), (By.ID,"sap-login-submit"),
        (By.CSS_SELECTOR,"button[type='submit']"),
        (By.XPATH,"//button[contains(., 'Logon') or contains(., 'Login')]"),
        (By.XPATH,"//input[@type='submit' or @value='Logon' or @value='Login')]")
    ]

    u = first_present(driver, user_fields, timeout=20)
    p = first_present(driver, pass_fields, timeout=20)
    if not (u and p):
        dump_artifacts(driver, "02_login_fields_not_found")
        raise SystemExit("Could not find username/password fields – check SSO/VPN requirements or page layout.")

    u[0].clear(); u[0].send_keys(SAP_USERNAME)
    p[0].clear(); p[0].send_keys(SAP_PASSWORD)

    btn = first_present(driver, login_btns, timeout=5)
    btn[0].click() if btn else p[0].submit()

    time.sleep(3)
    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState")=="complete")
    dump_artifacts(driver, "03_after_login")
    assert_not_auth_error(driver, "03_after_login")

def perform_task(driver):
    dump_artifacts(driver, "04_before_action")
    assert_not_auth_error(driver, "04_before_action")
    # TODO: add your real SAP steps here once access is confirmed
    time.sleep(1)
    dump_artifacts(driver, "05_after_action")
    assert_not_auth_error(driver, "05_after_action")

def main():
    start_ts = time.strftime("%Y-%m-%d %H:%M:%S")
    ok, err = False, ""
    d = make_driver()
    try:
        login_to_sap(d)
        perform_task(d)
        ok = True
    except SystemExit as e:
        err = str(e); traceback.print_exc()
    except Exception:
        err = traceback.format_exc(); dump_artifacts(d,"99_exception"); traceback.print_exc()
    finally:
        try: d.quit()
        except: pass
    end_ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(("SUCCESS" if ok else "FAILED"), start_ts, "→", end_ts)
    sys.exit(0 if ok else 1)

if __name__=="__main__":
    main()
