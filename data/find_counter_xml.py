"""
Tim XML request pattern cho Toshiba counter trong JS bundle
"""
import requests
import re

base = 'http://192.168.0.183'
h = {'User-Agent': 'Mozilla/5.0'}

r = requests.get(base + '/topaccess.e49ee3eefb40b1c28871.bundle.js?v=1680758417ta', headers=h, timeout=15)
js = r.text
print(f"JS bundle size: {len(js)} chars")

# --- Tim gblGETRequestXMLArray lien quan counter ---
print('\n=== gblGETRequestXMLArray (counter-related) ===')
pattern = r'gblGETRequestXMLArray\s*=\s*\[([^\]]{0,600})\]'
for m in re.findall(pattern, js):
    if 'ount' in m.lower():
        print(m[:400])
        print('---')

# --- Tim glbContentWebServerCmdArray lien quan counter ---
print('\n=== glbContentWebServerCmdArray (counter-related) ===')
pattern2 = r'glbContentWebServerCmdArray\s*=\s*\[([^\]]{0,600})\]'
for m in re.findall(pattern2, js):
    if 'ount' in m.lower():
        print(m[:400])
        print('---')

# --- Tim GET Request XML cho TotalCounter page ---
print('\n=== GET XML related to TotalCounter ===')
# Tim trong cac doan co "TotalCounter" hoac "totalCounter"
idx = 0
while True:
    pos = js.find('TotalCounter', idx)
    if pos == -1:
        break
    snippet = js[max(0, pos-300):pos+300]
    if 'gblGET' in snippet or 'CmdArray' in snippet or 'xpath' in snippet.lower():
        print(f"--- at pos {pos} ---")
        print(snippet)
        print()
    idx = pos + 1

# --- Tim XPath voi counter ---
print('\n=== XPaths containing Counter ===')
# Tim cac xpath string
for pat in [r'"([^"]*Counter[^"]*)"', r"'([^']*Counter[^']*?)'"]:
    for m in re.findall(pat, js):
        if '/' in m and 'Counter' in m and len(m) < 100:
            print(f"  {m}")
