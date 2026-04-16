"""
Xem cau truc chi tiet rightPane - noi chua counter data
"""
import sys
sys.path.insert(0, 'd:/Data/CT QL Photocopy/Agent/Agent V4')

import logging
logging.basicConfig(level=logging.WARNING)

from core.counter_engine import fetch_selenium
from bs4 import BeautifulSoup

url = 'http://192.168.0.183/#/counter/TotalCounter'
html = fetch_selenium(url)

if html:
    soup = BeautifulSoup(html, 'lxml')
    right_pane = soup.find(id='rightPane')
    if right_pane:
        print("=== rightPane HTML ===")
        print(right_pane.prettify()[:8000])
    else:
        print("rightPane not found!")
        # Tim tat ca tables
        for table in soup.find_all('table'):
            print("=== TABLE ===")
            print(table.prettify()[:2000])
            print()
