"""
Script debug v2: Tim hieu Toshiba TopAccess /contentwebserver endpoint
"""
import requests
import json

base = 'http://192.168.0.183'
headers_base = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'http://192.168.0.183/',
    'Origin': 'http://192.168.0.183',
}

print("=" * 60)
print("PROBING /contentwebserver endpoint")
print("=" * 60)

# GET request
print("\n[1] GET /contentwebserver")
try:
    r = requests.get(base + '/contentwebserver', headers=headers_base, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# POST request - nen la JSON
print("\n[2] POST /contentwebserver (empty)")
try:
    r = requests.post(base + '/contentwebserver', headers={**headers_base, 'Content-Type': 'application/json'}, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# POST request voi payload counter
print("\n[3] POST /contentwebserver (counter payload guess)")
payloads = [
    {"command": "getCounter"},
    {"type": "counter"},
    {"action": "TotalCounter"},
    {"cmd": "counter", "path": "/counter/TotalCounter"},
    [{"command": "getCounter"}],
]
for payload in payloads:
    try:
        r = requests.post(
            base + '/contentwebserver',
            headers={**headers_base, 'Content-Type': 'application/json'},
            json=payload,
            timeout=5
        )
        print(f"  Payload {str(payload)[:50]}: status={r.status_code}, size={len(r.text)}")
        if r.status_code == 200:
            print(f"  Response: {r.text[:300]}")
    except Exception as e:
        print(f"  Error: {e}")

# Thu fetch JS bundle de tim counter endpoint
print("\n\n[4] Searching JS bundles for counter API patterns...")
try:
    r = requests.get(base + '/', headers=headers_base, timeout=5)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, 'lxml')
    scripts = soup.find_all('script', src=True)
    print(f"Found {len(scripts)} script tags")
    for s in scripts:
        src = s.get('src', '')
        print(f"  Script: {src}")
except Exception as e:
    print(f"Error: {e}")
