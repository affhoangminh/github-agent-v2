import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer  # dùng để delay

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
    # seed_data()

    print("✅ Database reset complete")


# ================= SEED DATA =================
def seed_data():
    # ===== ĐƠN VỊ =====
    query("""
    INSERT INTO danh_muc_don_vi (
        code_don_vi, name_don_vi, address_don_vi,
        contact_name, contact_phone,
        ward_don_vi, city_don_vi,
        license, hardware_id, id_donvi
    )
    VALUES (
        'DV001',
        'Công ty Demo',
        'Thái Nguyên',
        'Admin',
        '0123456789',
        'Phường A',
        'Thái Nguyên',
        'LIC001',
        'HW001',
        1
    )
    """)

    # ===== METHOD =====
    query("""
    INSERT INTO danh_muc_method (
        code_method, name_method, path_method,
        parser_method, counter_method
    )
    VALUES
    ('R001', 'Ricoh IM Series',
     '/web/guest/en/websys/status/getUnificationCounter.cgi',
     'requests', 'RicohIM4000'),

    ('T001', 'Toshiba E Series',
     '/Counters/Counter.html',
     'requests', 'ToshibaE')
    """)

    # ===== MACHINE =====
    query("""
    INSERT INTO machine (
        code_machine, name_machine, serial_machine,
        location, note, counter_enabled,
        ip_machine, path_machine,
        max_days, times_per_day,
        code_method, raw_data, code_don_vi
    )
    VALUES
    ('M001', 'Ricoh IM 4000', '192.168.1.10',
     'Phòng Kế Toán', '', 1,
     '192.168.1.10',
     '/web/guest/en/websys/status/getUnificationCounter.cgi',
     30, 3, 'R001', '', 'DV001'),

    ('M002', 'Toshiba E3518A', '192.168.0.181',
     'Phòng Kinh Doanh', '', 1,
     '192.168.0.181',
     '/Counters/Counter.html',
     30, 3, 'T001', '', 'DV001')
    """)


# ================= MAIN =================
def main():
    # 🔥 nếu chưa có DB → tạo mới
    if not os.path.exists(DB_PATH):
        print("⚙️ First run → init database")
        init_db()
        seed_data()

    # ===== RUN UI =====
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # ✅ delay 5 giây rồi mới chạy counter (không block UI)
    QTimer.singleShot(5000, run_counter_once)

    sys.exit(app.exec())


# ================= RUN =================
if __name__ == "__main__":
    main()