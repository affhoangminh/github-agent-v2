import requests
import importlib
from datetime import datetime

from database.db import query
from core.logger import logger

# Selenium (nếu cần)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def fetch_requests(url):
    """Lấy nội dung HTML bằng thư viện requests."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            logger.error(f"HTTP ERROR: {res.status_code} at {url}")
            return None

        return res.text
    except Exception as e:
        logger.error(f"Requests error at {url}: {e}")
        return None


def fetch_selenium(url):
    """Lấy nội dung HTML bằng Selenium (headless mode)."""
    driver = None
    try:
        logger.info(f"Using Selenium for {url}")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        WebDriverWait(driver, 10).until(
            lambda d: d.page_source is not None
        )

        html = driver.page_source
        return html
    except Exception as e:
        logger.error(f"Selenium error at {url}: {e}")
        return None
    finally:
        if driver:
            driver.quit()


def _get_method(code_method):
    """Lấy thông tin phương thức từ DB."""
    methods = query(
        "SELECT * FROM danh_muc_method WHERE code_method = ?",
        (code_method,),
        fetch=True
    )
    if not methods:
        logger.warning(f"Không tìm thấy method: {code_method}")
        return None
    return methods[0]


def _parse_data(counter_method, raw_html):
    """Nạp động và gọi parser."""
    try:
        module_path = f"core.parsers.{counter_method}"
        parser_module = importlib.import_module(module_path)

        if not hasattr(parser_module, "parse"):
            raise AttributeError(f"Module {counter_method} thiếu hàm parse()")

        return parser_module.parse(raw_html)
    except Exception as e:
        logger.error(f"Lỗi parse với {counter_method}: {e}")
        return {
            "total": 0, "bw": 0, "color": 0,
            "copy": 0, "printer": 0, "scan": 0
        }


def _save_log(code_machine, result, raw_html):
    """Lưu kết quả counter vào database."""
    try:
        query("""
        INSERT INTO counter_log (
            code_machine, timestamp, total_counter, bw_counter,
            color_counter, copy_counter, printer_counter,
            scan_counter, raw_counter
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            code_machine,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            result.get("total", 0),
            result.get("bw", 0),
            result.get("color", 0),
            result.get("copy", 0),
            result.get("printer", 0),
            result.get("scan", 0),
            raw_html
        ))
        logger.info(f"Đã lưu counter cho máy: {code_machine}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu DB cho {code_machine}: {e}")
        return False


def process_machine(machine):
    """Xử lý lấy counter cho một máy cụ thể."""
    try:
        code_machine = machine["code_machine"]
        ip = machine["ip_machine"]
        path = machine["path_machine"]
        code_method = machine["code_method"]

        method = _get_method(code_method)
        if not method:
            return None

        url = f"http://{ip}{path}"
        parser_method = method["parser_method"]
        counter_method = method["counter_method"]

        # Fetch
        raw_html = fetch_selenium(url) if parser_method == "selenium" else fetch_requests(url)
        if not raw_html:
            return None

        # Parse
        result = _parse_data(counter_method, raw_html)
        
        # Save
        return _save_log(code_machine, result, raw_html)

    except Exception as e:
        logger.error(f"Lỗi hệ thống khi xử lý máy {machine.get('code_machine')}: {e}")
        return None


def run_counter_once():
    """Chạy tiến trình lấy counter cho tất cả các máy đang kích hoạt."""
    try:
        machines = query("""
            SELECT * FROM machine
            WHERE counter_enabled = 1
        """, fetch=True)

        logger.info(f"Bắt đầu chạy counter cho {len(machines)} máy")

        for machine in machines:
            process_machine(machine)
    except Exception as e:
        logger.error(f"Lỗi khi chạy run_counter_once: {e}")