from database.db import query
from strategies.ricoh_strategy import get_counter as ricoh
from strategies.toshiba_strategy import get_counter as toshiba

def fetch_counter(machine):
    ip = machine[4]  # serial field tạm dùng làm IP
    strategy = machine[6]

    if strategy == "RICOH":
        return ricoh(ip)
    elif strategy == "TOSHIBA":
        return toshiba(ip)

def save_counter(machine_id, data):
    query("""
    INSERT INTO counter_log (
        machine_id, timestamp, total, bw, color,
        copy, printer, scan, raw
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        machine_id,
        data["time"],
        data["total"],
        data["bw"],
        data["color"],
        data["copy"],
        data["printer"],
        data["scan"],
        data["raw"]
    ))