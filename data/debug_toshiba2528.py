"""
Script debug: Dung Selenium de bat network requests tu SPA Toshiba TopAccess.
Chay trong thread rieng voi hard timeout.
"""
import time
import json
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = 'http://192.168.0.183/#/counter/TotalCounter'
TIMEOUT = 25  # seconds

result = {"done": False, "html": None, "logs": [], "error": None}


def run_selenium():
    driver = None
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Bat performance logging de bat network requests
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(20)
        driver.set_script_timeout(20)

        print(f"Loading: {URL}")
        driver.get(URL)

        # Cho SPA render
        print("Waiting 6s for SPA to render...")
        time.sleep(6)

        # Lay rendered HTML
        result["html"] = driver.page_source

        # Lay network logs (bat API calls)
        logs = driver.get_log("performance")
        result["logs"] = logs
        result["done"] = True

        print(f"Got HTML: {len(result['html'])} chars")
        print(f"Got {len(logs)} network log entries")

    except Exception as e:
        result["error"] = str(e)
        print(f"Error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


t = threading.Thread(target=run_selenium, daemon=True)
t.start()
t.join(timeout=TIMEOUT + 5)

if t.is_alive():
    print(f"\nERROR: Selenium hung after {TIMEOUT+5}s! Giving up.")
    exit(1)

if result["error"]:
    print(f"\nSelenium error: {result['error']}")
    exit(1)

# --- Phan tich HTML ---
print("\n" + "=" * 60)
print("ANALYZING RENDERED HTML")
print("=" * 60)

html = result["html"]

# In phan body de xem cau truc
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "lxml")

# Tim tat ca phan tu co id
elements_with_id = soup.find_all(id=True)
print(f"\nElements with ID: {len(elements_with_id)}")
for el in elements_with_id[:50]:
    text = el.get_text(strip=True)[:80]
    print(f"  id='{el.get('id')}' tag={el.name} text='{text}'")

# Tim cac so (co the la counter)
print("\n\nLooking for numeric values in table cells / spans...")
for tag in soup.find_all(['td', 'span', 'div', 'p']):
    text = tag.get_text(strip=True)
    if text.isdigit() and int(text) > 100:
        parent = tag.parent
        print(f"  <{tag.name}> id='{tag.get('id')}' class='{tag.get('class')}' value={text}")

# Tim keyword lien quan
print("\n\nSearching for counter-related text...")
counter_keywords = ['Total', 'Counter', 'Black', 'Color', 'Copy', 'Print', 'Scan']
for td in soup.find_all(['td', 'th', 'span', 'div', 'label']):
    text = td.get_text(strip=True)
    for kw in counter_keywords:
        if kw.lower() in text.lower() and len(text) < 100:
            print(f"  <{td.name}> id='{td.get('id')}' class='{td.get('class')}' text='{text}'")
            break

# Phan tich network logs de tim API calls
print("\n\n" + "=" * 60)
print("NETWORK API CALLS (JSON responses)")
print("=" * 60)
for log in result["logs"]:
    try:
        msg = json.loads(log["message"])["message"]
        if msg.get("method") == "Network.responseReceived":
            url = msg["params"]["response"]["url"]
            ct = msg["params"]["response"].get("mimeType", "")
            if "json" in ct or "counter" in url.lower() or "api" in url.lower():
                print(f"  URL: {url}")
                print(f"  Content-Type: {ct}")
                print()
    except Exception:
        pass

print("\n=== RAW HTML BODY (first 3000 chars) ===")
body = soup.find('body')
if body:
    print(body.prettify()[:3000])
