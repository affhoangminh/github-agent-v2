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
from core.counter_engine import run_counter_once, load_unit_config, cleanup_old_logs


DB_PATH = "data/agent.db"


# ================= SCHEDULING =================
def start_auto_timer(window):
    """Tính toán và lập lịch chạy counter tự động."""
    config = load_unit_config()
    times_per_day = config.get("times_per_day", 3)
    
    # Công thức: 8 giờ / số lần = khoảng cách mỗi lần chạy (giờ)
    interval_hours = 8.0 / max(1, times_per_day)
    interval_ms = int(interval_hours * 3600 * 1000)
    
    logger.info("📅 Lập lịch tự động: Quét mỗi %.1f giờ (Tần suất: %d lần/8h)", interval_hours, times_per_day)
    
    # Tạo timer chạy lặp lại
    timer = QTimer(window)
    timer.timeout.connect(window.trigger_counter)
    timer.start(interval_ms)
    
    # Lưu reference để không bị garbage collected
    window._auto_timer = timer

# ================= MAIN =================
def main():
    if not os.path.exists(DB_PATH):
        logger.info("First run → initializing database")
        init_db()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # 1. Dọn dẹp log cũ ngay khi khởi động
    cleanup_old_logs()

    # 2. Chạy counter lần đầu sau 5 giây
    QTimer.singleShot(5000, window.trigger_counter)

    # 3. Bắt đầu bộ lập lịch tự động
    start_auto_timer(window)

    sys.exit(app.exec())


# ================= RUN =================
if __name__ == "__main__":
    main()