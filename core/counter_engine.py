import requests
import importlib
import socket
import logging
import threading
from datetime import datetime

from database.db import query

# Selenium (nếu cần)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)


# ==============================
# CHECK IP ALIVE
# ==============================
def is_ip_alive(ip, port=80, timeout=2): # Tăng timeout mặc định lên 2s
    try:
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        return True
    except OSError:
        return False


# ==============================
# FETCH HTML (REQUESTS)
# ==============================
def fetch_requests(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5) # Tăng timeout lên 5s

        if res.status_code != 200:
            logger.error("HTTP error %s for URL: %s", res.status_code, url)
            return None

        return res.text

    except requests.RequestException as e:
        logger.error("Requests error for %s: %s", url, e)
        return None


# ==============================
# FETCH HTML (SELENIUM)
# ==============================
SELENIUM_TIMEOUT = 30  # Tổng timeout (giây) cho toàn bộ quá trình Selenium

# CSS selector de kiem tra trang Toshiba TopAccess SPA da render counter xong
# (dung class thay vi element ID vi SPA khong dung ID cho cac o du lieu)
_TOSHIBA_READY_SELECTOR = "div.print-counter table tbody tr td:not(.labelled)"


def _dismiss_alerts(driver, max_attempts=5):
    """Dismiss tất cả JS alert đang mở, trả về số lượng đã dismiss."""
    from selenium.common.exceptions import NoAlertPresentException
    dismissed = 0
    for _ in range(max_attempts):
        try:
            alert = driver.switch_to.alert
            msg = alert.text[:120] if alert.text else "(no text)"
            logger.debug("Dismissing JS alert: %s", msg)
            alert.dismiss()
            dismissed += 1
            import time
            time.sleep(0.3)
        except NoAlertPresentException:
            break
        except Exception as e:
            logger.debug("Alert dismiss error: %s", e)
            break
    return dismissed


def fetch_selenium(url):
    """
    Fetch HTML từ SPA Toshiba TopAccess bằng Selenium.
    """
    import time as _time
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoAlertPresentException
    result_container = {"html": None, "error": None}

    # Tách base URL (không có hash)
    base_url = url.split("/#")[0] if "/#" in url else url

    def _run():
        driver = None
        try:
            logger.debug("Using Selenium for: %s", url)

            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--blink-settings=imagesEnabled=false")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")

            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(SELENIUM_TIMEOUT)
            driver.set_script_timeout(SELENIUM_TIMEOUT)

            # Bước 1: Load trang gốc để lấy session cookie
            try:
                driver.get(base_url)
                _time.sleep(2)
                _dismiss_alerts(driver)
            except Exception:
                pass

            # Bước 2: Navigate tới trang counter
            driver.get(url)

            # Bước 3: Đợi một chút và kiểm tra Alert (thường là Session Timeout ở đây)
            _time.sleep(2)
            dismissed = _dismiss_alerts(driver)
            
            if dismissed > 0:
                _time.sleep(3)
                driver.refresh()
                _time.sleep(2)
                _dismiss_alerts(driver)

            # Bước 4: Chờ SPA render dữ liệu
            _time.sleep(3)
            _dismiss_alerts(driver)

            # Kiểm tra nhanh xem counter table đã render chưa
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, _TOSHIBA_READY_SELECTOR)
                has_data = any(
                    el.text.strip().replace(",", "").isdigit()
                    for el in elements
                    if el.text.strip()
                )
                if not has_data:
                    _time.sleep(5)
                    _dismiss_alerts(driver)
            except Exception:
                pass

            result_container["html"] = driver.page_source


        except TimeoutException:
            result_container["error"] = f"Page load timeout sau {SELENIUM_TIMEOUT}s"
        except WebDriverException as e:
            result_container["error"] = f"WebDriver error: {e}"
        except Exception as e:
            result_container["error"] = f"Unexpected error: {e}"
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=SELENIUM_TIMEOUT + 15)

    if t.is_alive():
        logger.error("Selenium bị treo cho URL: %s", url)
        result_container["error"] = "Trình duyệt bị treo"

    if result_container["error"]:
        logger.error("Selenium error: %s", result_container["error"])
        return None

    return result_container["html"]


# ==============================
# BUILD URL FROM MACHINE
# ==============================
def build_url(machine):
    ip = machine["ip_machine"]
    path = machine["path_machine"]
    return f"http://{ip}{path}"


# ==============================
# LOAD METHOD FROM DB
# ==============================
def load_method(code_method):
    rows = query(
        "SELECT * FROM danh_muc_method WHERE code_method = ?",
        (code_method,),
        fetch=True
    )
    if not rows:
        return None
    return rows[0]


# ==============================
# FETCH HTML (DISPATCH)
# ==============================
def fetch_html(parser_method, url):
    if parser_method.lower() == "selenium":
        return fetch_selenium(url)
    return fetch_requests(url)


# ==============================
# PARSE HTML DYNAMICALLY
# ==============================
def parse_html(counter_method, raw_html):
    try:
        module_path = f"core.parsers.{counter_method}"
        module = importlib.import_module(module_path)
        if not hasattr(module, "parse"): return None
        return module.parse(raw_html)
    except Exception as e:
        logger.error("Parser '%s' error: %s", counter_method, e)
        return None


# ==============================
# SAVE RESULT TO DB
# ==============================
def save_result(code_machine, result, raw_html):
    query("""
    INSERT INTO counter_log (
        code_machine, timestamp,
        total_counter, bw_counter, color_counter,
        copy_counter, printer_counter, scan_counter,
        raw_counter
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        code_machine,
        str(datetime.now()),
        result.get("total", 0),
        result.get("bw", 0),
        result.get("color", 0),
        result.get("copy", 0),
        result.get("printer", 0),
        result.get("scan", 0),
        raw_html
    ))
    logger.info("Saved counter log for machine: %s", code_machine)


# ==============================
# FETCH + PARSE 1 MACHINE
# ==============================
def process_machine(machine):
    code_machine = machine["code_machine"]
    ip = machine["ip_machine"]

    if not is_ip_alive(ip):
        logger.warning("IP %s not reachable — skipping machine %s", ip, code_machine)
        return None

    method = load_method(machine["code_method"])
    if not method: return None

    url = build_url(machine)
    parser_method = method["parser_method"]
    counter_method = method["counter_method"]

    raw_html = fetch_html(parser_method, url)
    if not raw_html: return None

    result = parse_html(counter_method, raw_html)
    if not result: return None

    save_result(code_machine, result, raw_html)
    return True


# ==============================
# RUN ALL MACHINES
# ==============================
def run_counter_once(on_machine_finished=None, on_progress=None):
    machines = query("""
        SELECT * FROM machine
        WHERE counter_enabled = 1
    """, fetch=True)

    total_m = len(machines)
    if on_progress:
        on_progress(f"Bắt đầu lấy counter cho {total_m} máy...")

    for idx, machine in enumerate(machines):
        code = machine["code_machine"]
        name = machine["name_machine"]
        ip = machine["ip_machine"]
        
        if on_progress:
            on_progress(f"🚀 Lấy số counter máy {name} - IP: {ip} ({idx+1}/{total_m})")
            
        success = process_machine(machine)
        
        if on_machine_finished:
            on_machine_finished(code, success is not None)
            
    if on_progress:
        on_progress(f"✅ Đã hoàn tất chu trình cho {total_m} máy.")