import time
from database.db import query
from core.counter_engine import fetch_counter, save_counter

def run_scheduler():
    print("🚀 Scheduler started")

    while True:
        machines = query("SELECT * FROM machine", fetch=True)

        for m in machines:
            data = fetch_counter(m)
            if data:
                save_counter(m[0], data)
                print(f"✅ Saved counter for {m[2]}")

        time.sleep(300)  # 5 phút