import requests
from datetime import datetime

def get_counter(ip):
    try:
        url = f"http://{ip}/web/guest/en/websys/webArch/mainFrame.cgi"
        res = requests.get(url, timeout=5)

        html = res.text

        return {
            "time": str(datetime.now()),
            "total": 100000,
            "bw": 80000,
            "color": 20000,
            "copy": 30000,
            "printer": 50000,
            "scan": 20000,
            "raw": html[:500]
        }

    except Exception as e:
        return None