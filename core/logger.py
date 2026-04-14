import logging
import os

# Đường dẫn file log
LOG_FILE = "agent.log"

def setup_logger():
    """Thiết lập cấu hình logging tập trung."""
    logger = logging.getLogger("AgentV3")
    logger.setLevel(logging.DEBUG)

    # Nếu đã có handler thì không thêm nữa (tránh trùng lặp)
    if logger.handlers:
        return logger

    # Định dạng log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler ghi ra Console (INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler ghi ra File (DEBUG)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Khởi tạo logger dùng chung cho toàn bộ module core
logger = setup_logger()
