from datetime import datetime

def get_counter(ip):
    return {
        "time": str(datetime.now()),
        "total": 50000,
        "bw": 40000,
        "color": 10000,
        "copy": 20000,
        "printer": 20000,
        "scan": 10000,
        "raw": "TOSHIBA RAW"
    }