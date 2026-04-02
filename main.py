import sys
import os

from PySide6.QtWidgets import QApplication

from database.init_db import init_db
from database.db import query
from ui.main_window import MainWindow
from core.counter_engine import run_counter_once


DB_PATH = "data/agent.db"


# ================= RESET DB =================
def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Deleted old database")

    init_db()
    seed_data()

    print("✅ Database reset complete")


# ================= SEED DATA =================
def seed_data():
    # phương thức lấy data
    query("""
    INSERT INTO data_method (code, name, data_url, raw_type, parser)
    VALUES
    ('R001', 'Ricoh IM Series', '/web/guest/en/websys/status/getUnificationCounter.cgi', 'HTML', 'ricoh_parser'),
    ('T001', 'Toshiba E Series', '/Counters/Counter.html', 'HTML', 'toshiba_parser')
    """)

    # máy demo
    query("""
    INSERT INTO machine (
        org_id, machine_code, name, serial,
        storage_code, max_days, times_per_day, note,
        location, method_code, data_url, counter_parser, raw_data
    ) VALUES
    (1, 'R001', 'Photocopy Ricoh IM 4000', '192.168.1.10',
     'RICOH', 30, 3, '',
     'Phòng Kế Toán', 'R001',
     '/web/guest/en/websys/status/getUnificationCounter.cgi',
     'ricoh_parser', ''),

    (1, 'T001', 'Photocopy Toshiba E3518A', '192.168.0.181',
     'TOSHIBA', 30, 3, '',
     'Phòng Kinh Doanh', 'T001',
     '/Counters/Counter.html',
     'toshiba_parser', '')
    """)


# ================= MAIN =================
def main():
    # 🔥 nếu chưa có DB → tạo mới
    if not os.path.exists(DB_PATH):
        print("⚙️ First run → init database")
        init_db()
        seed_data()

    else:
        print("✅ Database exists")

    # 🚫 KHÔNG chạy scheduler (UI mode)
    print("🛑 Scheduler OFF (UI Mode)")

    # ===== RUN UI =====
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    run_counter_once()

    sys.exit(app.exec())


# ================= RUN =================
if __name__ == "__main__":
    main()