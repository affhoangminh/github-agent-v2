import requests
from datetime import datetime
from database.db import query
from core.engine import parse_counter


def fetch_counter(machine):
    try:
        ip = machine[5]
        data_url = machine[6]
        parser_name = machine[12]

        url = f"http://{ip}{data_url}"
        print("FULL URL:", url)

        res = requests.get(url, timeout=5)
        html = res.text

        data = parse_counter(html, parser_name)

        data["time"] = str(datetime.now())
        data["raw"] = html[:500]

        return data

    except Exception as e:
        print("❌ Fetch error:", e)
        return None


def save_counter(machine_id, data):
    print("🔥 SAVING TO DB:", data)

    query("""
    INSERT INTO counter_log (
        machine_id, timestamp, total, bw, color,
        copy, printer, scan, raw
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        machine_id,
        data.get("time"),
        data.get("total", 0),
        data.get("bw", 0),
        data.get("color", 0),
        data.get("copy", 0),
        data.get("printer", 0),
        data.get("scan", 0),
        data.get("raw", "")
    ))


# 🔥 CORE SERVICE (dùng chung cho UI + scheduler)
def run_counter_once():
    machines = query("SELECT * FROM machine", fetch=True) or []

    print("👉 TOTAL MACHINES:", len(machines))

    results = []

    for m in machines:
        print("\n===== RUN MACHINE =====")

        data = fetch_counter(m)

        if data:
            save_counter(m[0], data)
            results.append((m, data))
        else:
            print("❌ No data")

    return results