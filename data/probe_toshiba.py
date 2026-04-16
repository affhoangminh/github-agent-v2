import requests

base = 'http://192.168.0.183'
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'http://192.168.0.183/'
}

# Cac API endpoint pho bien cua Toshiba TopAccess (React SPA)
endpoints = [
    '/counter.csv',
    '/CounterService/counter',
    '/api/counter',
    '/Cntr/counter',
    '/Data/CounterResultCSV.csv',
    '/CounterResultCSV.csv',
    '/counterdata',
    '/DeviceStatusService/DeviceStatus.csv',
    '/DeviceStatusService/DeviceStatus',
    '/cntr/CounterListJson',
    '/CounterList',
    '/CounterListJson',
    '/api/v1/counter',
    '/rest/counter',
    '/cgi-bin/counter',
    '/status/counter',
]

print("Probing Toshiba TopAccess API endpoints...")
print("=" * 60)

for ep in endpoints:
    try:
        r = requests.get(base + ep, timeout=4, headers=headers)
        ct = r.headers.get('Content-Type', '')
        print(f'[{r.status_code}] {ep}')
        print(f'    Content-Type: {ct}')
        print(f'    Size: {len(r.text)} chars')
        if r.status_code == 200 and len(r.text) > 50:
            print(f'    Preview: {r.text[:400]}')
        print()
    except Exception as e:
        print(f'[ERR] {ep} -> {e}')
        print()
