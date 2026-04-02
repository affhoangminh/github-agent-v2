import requests
from datetime import datetime

from core.parsers import parse_counter

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


# ==============================
# FETCH TOSHIBA (Selenium)
# ==============================
def fetch_toshiba(url):
    print("🔥 USING SELENIUM FOR TOSHIBA")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    driver.get(url)

    # 🔥 FIX QUAN TRỌNG: chờ HTML có counter thật
    WebDriverWait(driver, 10).until(
        lambda d: "Print_Total_TotalCounter_Total" in d.page_source
    )

    html = driver.page_source

    driver.quit()

    return html


# ==============================
# FETCH RICOH (requests)
# ==============================
def fetch_ricoh(url):
    print("🔥 USING REQUESTS")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers, timeout=10)

    print("Status:", res.status_code)

    if res.status_code != 200:
        return None

    return res.text


# ==============================
# MAIN FETCH ENGINE
# ==============================
def fetch_counter(machine):
    try:
        ip = machine[5]
        data_url = machine[6]
        parser_name = machine[12]

        url = f"http://{ip}{data_url}"

        print("\n===== RUN MACHINE =====")
        print("FULL URL:", url)
        print("👉 Load parser:", parser_name)

        # =========================
        # CHỌN DRIVER
        # =========================
        if "toshiba" in parser_name.lower():
            html = fetch_toshiba(url)
        else:
            html = fetch_ricoh(url)

        if not html:
            print("❌ Không lấy được HTML")
            return None

        # =========================
        # PARSE
        # =========================
        data = parse_counter(html, parser_name)

        print("👉 Parse result:", data)

        # =========================
        # ADD META
        # =========================
        data["time"] = str(datetime.now())

        # 🔥 FIX QUAN TRỌNG: lưu FULL RAW
        data["raw"] = html

        return data

    except Exception as e:
        print("❌ Fetch error:", e)
        return None
    
from database.db import query

def run_counter_once():
    machines = query("SELECT * FROM machine", fetch=True)

    print("👉 TOTAL MACHINES:", len(machines))

    for machine in machines:
        result = fetch_counter(machine)

        if result:
            print("🔥 SAVING TO DB:", result)

            query("""
                INSERT INTO counter_log 
                (machine_id, timestamp, total, bw, color, copy, printer, scan, raw)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                machine[0],  # id
                result["time"],
                result.get("total", 0),
                result.get("bw", 0),
                result.get("color", 0),
                result.get("copy", 0),
                result.get("printer", 0),
                result.get("scan", 0),
                result.get("raw", "")
            ))

        else:
            print("❌ FAIL MACHINE:", machine[0])