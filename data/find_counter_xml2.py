"""
Tim XML GET request body cho TotalCounter va thu POST len contentwebserver
"""
import requests
import re
import xml.dom.minidom

base = 'http://192.168.0.183'
h = {'User-Agent': 'Mozilla/5.0'}

r = requests.get(base + '/topaccess.e49ee3eefb40b1c28871.bundle.js?v=1680758417ta', headers=h, timeout=15)
js = r.text

# --- Tim gblGETRequestXMLArray ---
print('=== gblGETRequestXMLArray (all matches, first 30) ===')
pattern = r'gblGETRequestXMLArray\s*=\s*\[("[^"]{0,1000}"(?:,"[^"]{0,1000}")*)\]'
for i, m in enumerate(re.findall(pattern, js)[:30]):
    print(f"Match {i}: {m[:300]}")
    print('---')

# --- Tim GET request XML trong context TotalCounter ---
print('\n\n=== Searching TotalCounter context ===')
pos = 0
count = 0
while count < 20:
    idx = js.find('TotalCounter', pos)
    if idx == -1:
        break
    snippet = js[max(0, idx-500):idx+500]
    if 'gblGET' in snippet or 'XMLArray' in snippet or 'Counters/' in snippet:
        print(f"--- pos {idx} ---")
        print(snippet[:600])
        print()
        count += 1
    pos = idx + 1

# --- Thu POST len contentwebserver voi XML ---
print('\n\n=== Trying POST to /contentwebserver with counter XML ===')

# Toshiba TopAccess thuong dung request nay de lay counter
xml_requests = [
    # Format 1: GetValue voi XPath
    '<?xml version="1.0" encoding="utf-8"?><GetValue><XPath>Counters</XPath></GetValue>',

    # Format 2: GetValue cho tung XPath
    '<?xml version="1.0" encoding="utf-8"?><GetValue><XPath>Counters/Printer/Total/TotalCount</XPath></GetValue>',

    # Format 3: Multiple XPaths
    '''<?xml version="1.0" encoding="utf-8"?>
<GetValue>
<XPath>Counters/Printer/Total/TotalCount</XPath>
<XPath>Counters/Printer/Total/blackPageCount</XPath>
<XPath>Counters/Printer/CopyCounter/Total/TotalCount</XPath>
<XPath>Counters/Printer/PrintCounter/Total/TotalCount</XPath>
<XPath>Counters/Scanner/Total/TotalCount</XPath>
</GetValue>''',

    # Format 4: GetOnlyCounters command
    '<GetCounters><commandNode>Counters</commandNode></GetCounters>',
]

headers_post = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'text/xml; charset=utf-8',
    'Referer': 'http://192.168.0.183/',
    'Origin': 'http://192.168.0.183',
    'Accept': 'text/xml, application/xml, */*',
}

for i, xml_body in enumerate(xml_requests):
    try:
        r2 = requests.post(
            base + '/contentwebserver',
            data=xml_body.encode('utf-8'),
            headers=headers_post,
            timeout=5
        )
        print(f"\n[Request {i+1}] Status: {r2.status_code}")
        print(f"Content-Type: {r2.headers.get('Content-Type')}")
        if r2.status_code == 200 and r2.text.strip():
            print(f"Response ({len(r2.text)} chars): {r2.text[:500]}")
        else:
            print(f"Response: {r2.text[:200]}")
    except Exception as e:
        print(f"[Request {i+1}] Error: {e}")
