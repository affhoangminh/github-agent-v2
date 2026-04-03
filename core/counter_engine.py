import requests
import importlib
from datetime import datetime

from database.db import query

# Selenium (nếu cần)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


# ==============================
# FETCH HTML (REQUESTS)
# ==============================
def fetch_requests(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            print("❌ HTTP ERROR:", res.status_code)
            return None

        return res.text

    except Exception as e:
        print("❌ Requests error:", e)
        return None


# ==============================
# FETCH HTML (SELENIUM)
# ==============================
def fetch_selenium(url):
    try:
        print("🔥 USING SELENIUM")

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        WebDriverWait(driver, 10).until(
            lambda d: d.page_source is not None
        )

        html = driver.page_source
        driver.quit()

        return html

    except Exception as e:
        print("❌ Selenium error:", e)
        return None


# ==============================
# FETCH + PARSE 1 MACHINE
# ==============================
def process_machine(machine):
    try:
        print("\n===== RUN MACHINE =====")

        code_machine = machine["code_machine"]
        ip = machine["ip_machine"]
        path = machine["path_machine"]
        code_method = machine["code_method"]

        # =========================
        # LẤY METHOD
        # =========================
        method = query(
            "SELECT * FROM danh_muc_method WHERE code_method = ?",
            (code_method,),
            fetch=True
        )

        if not method:
            print("❌ Không tìm thấy method:", code_method)
            return None

        method = method[0]

        parser_method = method["parser_method"]      # requests / selenium
        counter_method = method["counter_method"]    # tên file parser

        # =========================
        # BUILD URL
        # =========================
        url = f"http://{ip}{path}"

        print("👉 URL:", url)
        print("👉 parser_method:", parser_method)
        print("👉 counter_method:", counter_method)

        # =========================
        # FETCH HTML
        # =========================
        if parser_method == "selenium":
            raw_html = fetch_selenium(url)
        else:
            raw_html = fetch_requests(url)

        if not raw_html:
            print("❌ Không lấy được HTML")
            return None

        # =========================
        # PARSE (DYNAMIC IMPORT)
        # =========================
        module_path = f"core.parsers.{counter_method}"

        parser_module = importlib.import_module(module_path)

        if not hasattr(parser_module, "parse"):
            raise Exception(f"{counter_method} thiếu hàm parse()")

        result = parser_module.parse(raw_html)

        print("👉 RESULT:", result)

        # =========================
        # SAVE DB
        # =========================
        query("""
        INSERT INTO counter_log (
            code_machine,
            timestamp,
            total_counter,
            bw_counter,
            color_counter,
            copy_counter,
            printer_counter,
            scan_counter,
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

        print("✅ Saved:", code_machine)

        return True

    except Exception as e:
        print("❌ PROCESS ERROR:", e)
        return None


# ==============================
# RUN ALL MACHINES
# ==============================
def run_counter_once():
    machines = query("""
        SELECT * FROM machine
        WHERE counter_enabled = 1
    """, fetch=True)

    print("👉 TOTAL MACHINES:", len(machines))

    for machine in machines:
        process_machine(machine)