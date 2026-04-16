import importlib
import socket
import logging
import threading
from datetime import datetime
from database.db import query

logger = logging.getLogger(__name__)

# ==============================
# UNIT CONFIG & LOG CLEANUP
# ==============================
def load_unit_config():
    """Lấy cấu hình chung (max_days, times_per_day) của đơn vị."""
    rows = query("SELECT max_days, times_per_day FROM danh_muc_don_vi WHERE id_donvi=1", fetch=True)
    return rows[0] if rows else {"max_days": 30, "times_per_day": 3}

def cleanup_old_logs():
    """Xóa log cũ dựa trên số ngày lưu trữ cấu hình trong DB."""
    config = load_unit_config()
    max_days = config.get("max_days", 30)
    
    query("""
        DELETE FROM counter_log 
        WHERE date(timestamp) < date('now', '-' || ? || ' day')
    """, (max_days,))
    logger.info("🧹 Đã dọn dẹp log cũ (Giới hạn lưu trữ: %d ngày)", max_days)
def is_ip_alive(ip, port=80, timeout=2.5):
    try:
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        return True
    except OSError:
        return False

# ==============================
# BUILD URL FROM MACHINE
# ==============================
def build_url(machine):
    ip = machine["ip_machine"]
    path = machine["path_machine"]
    return f"http://{ip}{path}"

# ==============================
# LOAD METHOD FROM DB
# ==============================
def load_method(code_method):
    rows = query("SELECT * FROM danh_muc_method WHERE code_method = ?", (code_method,), fetch=True)
    return rows[0] if rows else None

# ==============================
# FETCH HTML (DYNAMIC ENGINE LOADING)
# ==============================
def fetch_html(engine_name, url):
    """Nạp động Engine (requests, selenium, v.v.) từ thư mục core/engines/"""
    try:
        # Chuyển tên engine về chữ thường để khớp với tên file .py
        engine_name = engine_name.lower().strip()
        module_path = f"core.engines.{engine_name}"
        engine = importlib.import_module(module_path)
        if hasattr(engine, "fetch"):
            return engine.fetch(url)
        else:
            logger.error("Engine '%s' does not have a fetch(url) function", engine_name)
            return None
    except Exception as e:
        logger.error("Could not load engine '%s': %s", engine_name, e)
        return None

# ==============================
# PARSE HTML DYNAMICALLY
# ==============================
def parse_html(counter_method, raw_html):
    try:
        # Chuyển tên parser về chữ thường để khớp với tên file vật lý
        counter_method = counter_method.lower().strip()
        module_path = f"core.parsers.{counter_method}"
        module = importlib.import_module(module_path)
        if not hasattr(module, "parse"): return None
        return module.parse(raw_html)
    except Exception as e:
        logger.error("Parser '%s' error: %s", counter_method, e)
        return None

# ==============================
# SAVE RESULT TO DB
# ==============================
def save_result(code_machine, result, raw_html):
    query("""
    INSERT INTO counter_log (
        code_machine, timestamp,
        total_counter, bw_counter, color_counter,
        copy_counter, printer_counter, scan_counter,
        raw_counter
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        code_machine,
        str(datetime.now()),
        result.get("total", 0),
        result.get("bw", 0),
        result.get("color", 0),
        result.get("copy", 0),
        result.get("printer", 0),
        result.get("scan", 0),
        raw_html
    ))
    logger.info("Saved counter log for machine: %s", code_machine)

# ==============================
# FETCH + PARSE 1 MACHINE
# ==============================
def process_machine(machine):
    code_machine = machine["code_machine"]
    ip = machine["ip_machine"]

    if not is_ip_alive(ip):
        logger.warning("IP %s not reachable — skipping machine %s", ip, code_machine)
        return None

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            if attempt > 1:
                import time
                logger.info("Retrying machine %s (attempt %d/%d) in 10s...", code_machine, attempt, max_retries)
                time.sleep(10) # Chờ 10 giây trước khi thử lại

            method = load_method(machine["code_method"])
            if not method: return None

            url = build_url(machine)
            engine_name = method["parser_method"]
            parser_name = method["counter_method"]

            raw_html = fetch_html(engine_name, url)
            if not raw_html: 
                if attempt < max_retries: continue
                return None

            result = parse_html(parser_name, raw_html)
            if not result:
                if attempt < max_retries: continue
                return None

            save_result(code_machine, result, raw_html)
            return True

        except Exception as e:
            logger.error("Error processing machine %s on attempt %d: %s", code_machine, attempt, e)
            if attempt == max_retries: return None
    
    return None

# ==============================
# RUN ALL MACHINES
# ==============================
def run_counter_once(on_machine_finished=None, on_progress=None):
    machines = query("SELECT * FROM machine WHERE counter_enabled = 1", fetch=True)
    total_m = len(machines)
    if on_progress: on_progress(f"Bắt đầu lấy counter cho {total_m} máy...")

    for idx, machine in enumerate(machines):
        code = machine["code_machine"]
        name = machine["name_machine"]
        ip = machine["ip_machine"]
        if on_progress: on_progress(f"🚀 Lấy số counter máy {name} - IP: {ip} ({idx+1}/{total_m})")
        success = process_machine(machine)
        if on_machine_finished: on_machine_finished(code, success is not None)
            
    if on_progress: on_progress(f"✅ Đã hoàn tất chu trình cho {total_m} máy.")