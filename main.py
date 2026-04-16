import sys
import os
import logging

# ✅ Setup logging TRƯỚC KHI import bất kỳ module nào khác
from core.logger import setup_logging
setup_logging()

logger = logging.getLogger(__name__)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from database.init_db import init_db
from database.db import query
from ui.main_window import MainWindow
from core.counter_engine import run_counter_once


DB_PATH = "data/agent.db"


# ================= RESET DB =================
def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        logger.info("Deleted old database")

    init_db()
    logger.info("Database reset complete")


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

    logger.info("Seed data inserted")


# ================= MAIN =================
def main():
    if not os.path.exists(DB_PATH):
        logger.info("First run → initializing database")
        init_db()
        seed_data()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # Delay 5 giây rồi tự động chạy quét counter (thông qua hàm của window để hiện tiến trình)
    QTimer.singleShot(5000, window.trigger_counter)

    sys.exit(app.exec())


# ================= RUN =================
if __name__ == "__main__":
    main()