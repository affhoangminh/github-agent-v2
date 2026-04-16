"""
Xem page source thuc te cua Toshiba E2528A de hieu cau truc HTML
"""
import sys
sys.path.insert(0, 'd:/Data/CT QL Photocopy/Agent/Agent V4')

import logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

from core.counter_engine import fetch_selenium
from bs4 import BeautifulSoup

url = 'http://192.168.0.183/#/counter/TotalCounter'
html = fetch_selenium(url)

if html:
    soup = BeautifulSoup(html, 'lxml')
    body = soup.find('body')

    # In toan bo IDs trong page
    print("=== ALL ELEMENT IDs ===")
    for el in soup.find_all(id=True):
        text = el.get_text(strip=True)[:60]
        print(f"  id='{el.get('id')}' tag={el.name} text='{text}'")

    # Tim cac element co the chua so
    print("\n=== ELEMENTS WITH NUMBERS ===")
    for el in soup.find_all(['span', 'td', 'div', 'p', 'li']):
        text = el.get_text(strip=True)
        if text.replace(',', '').isdigit() and int(text.replace(',', '')) >= 0:
            eid = el.get('id', '')
            cls = ' '.join(el.get('class', []))[:50]
            print(f"  <{el.name}> id='{eid}' class='{cls}' value='{text}'")

    # In body HTML de xem cau truc
    print("\n=== BODY HTML (first 5000 chars) ===")
    if body:
        print(body.prettify()[:5000])
