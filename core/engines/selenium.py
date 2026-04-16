import logging
import threading
import time as _time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoAlertPresentException

logger = logging.getLogger(__name__)

SELENIUM_TIMEOUT = 30
_TOSHIBA_READY_SELECTOR = "div.print-counter table tbody tr td:not(.labelled)"

def _dismiss_alerts(driver, max_attempts=5):
    """Dismiss tất cả JS alert đang mở."""
    dismissed = 0
    for _ in range(max_attempts):
        try:
            alert = driver.switch_to.alert
            logger.debug("Dismissing JS alert: %s", alert.text[:120] if alert.text else "(no text)")
            alert.dismiss()
            dismissed += 1
            _time.sleep(0.3)
        except NoAlertPresentException:
            break
        except Exception:
            break
    return dismissed

def fetch(url):
    """Tải dữ liệu HTML bằng Selenium (Cho các trang Web App/SPA)."""
    result_container = {"html": None, "error": None}
    base_url = url.split("/#")[0] if "/#" in url else url

    def _run():
        driver = None
        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--blink-settings=imagesEnabled=false")

            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(SELENIUM_TIMEOUT)

            # Lấy session cookie
            try:
                driver.get(base_url)
                _time.sleep(2)
                _dismiss_alerts(driver)
            except Exception: pass

            driver.get(url)
            _time.sleep(2)
            if _dismiss_alerts(driver) > 0:
                _time.sleep(2)
                driver.refresh()
            
            _time.sleep(4) # Chờ render
            _dismiss_alerts(driver)

            result_container["html"] = driver.page_source

        except Exception as e:
            result_container["error"] = str(e)
        finally:
            if driver:
                try: driver.quit()
                except Exception: pass

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=SELENIUM_TIMEOUT + 15)

    if t.is_alive():
        logger.error("Selenium bị treo cho URL: %s", url)
        return None

    if result_container["error"]:
        logger.error("Selenium error: %s", result_container["error"])
        return None

    return result_container["html"]
