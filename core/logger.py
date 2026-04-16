"""
Centralized logging setup for Agent V4.
Call setup_logging() once in main.py before any other imports.
All modules use: logger = logging.getLogger(__name__)
"""
import logging
import os
from datetime import datetime


LOG_DIR = "data/logs"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def cleanup_old_logs(days=30):
    """Xóa các file log cũ hơn số ngày quy định."""
    try:
        if not os.path.exists(LOG_DIR):
            return

        now = datetime.now()
        for filename in os.listdir(LOG_DIR):
            if not filename.endswith(".log"):
                continue
            
            file_path = os.path.join(LOG_DIR, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # Tính số ngày chênh lệch
            diff = (now - file_time).days
            if diff > days:
                os.remove(file_path)
                logging.getLogger(__name__).info("Đã xóa file log cũ: %s (%d ngày)", filename, diff)
    except Exception as e:
        logging.getLogger(__name__).error("Lỗi khi dọn dẹp log: %s", e)


def setup_logging(level=logging.DEBUG):
    """Configure root logger: console + rotating daily file."""
    os.makedirs(LOG_DIR, exist_ok=True)

    # 1. Dọn dẹp log cũ trước
    cleanup_old_logs(days=30)

    # 2. Thiết lập log cho ngày hiện tại
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"agent_{today}.log")

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(),                          # console
            logging.FileHandler(log_file, encoding="utf-8"), # file
        ]
    )

    # Giữ 3rd-party libraries ở WARNING để không spam log
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("bs4").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging initialized → %s (level=%s)",
        log_file, logging.getLevelName(level)
    )
