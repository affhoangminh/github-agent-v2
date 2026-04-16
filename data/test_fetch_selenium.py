"""
Test fetch_selenium moi cho Toshiba E2528A
"""
import sys
sys.path.insert(0, 'd:/Data/CT QL Photocopy/Agent/Agent V4')

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

from core.counter_engine import fetch_selenium, parse_html

url = 'http://192.168.0.183/#/counter/TotalCounter'

print("=" * 60)
print(f"Testing fetch_selenium for: {url}")
print("=" * 60)

html = fetch_selenium(url)

if html:
    print(f"\nGot HTML: {len(html)} chars")

    # Kiem tra cac element ID co trong HTML khong
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')

    check_ids = [
        "Print_Total_TotalCounter_Total",
        "Print_Total_TotalCounter_Black",
        "Print_Total_CopyCounter_Total",
        "Print_Total_PrinterCounter_Total",
        "Scan_Total_TotalCounter_Total",
    ]
    print("\n=== Element ID Check ===")
    for eid in check_ids:
        el = soup.find(id=eid)
        if el:
            print(f"  FOUND  id='{eid}' -> value='{el.text.strip()}'")
        else:
            print(f"  MISSING id='{eid}'")

    # Ket qua parse
    print("\n=== Parse Result ===")
    result = parse_html('Toshiba2528', html)
    print(f"Result: {result}")
else:
    print("\nERROR: fetch_selenium returned None!")
