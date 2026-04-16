from database.db import query


def init_db():

    # ===== DANH MỤC ĐƠN VỊ =====
    query("""
    CREATE TABLE IF NOT EXISTS danh_muc_don_vi (
        code_don_vi TEXT PRIMARY KEY,
        name_don_vi TEXT,
        address_don_vi TEXT,
        contact_name TEXT,
        contact_phone TEXT,
        ward_don_vi TEXT,
        city_don_vi TEXT,
        license TEXT,
        hardware_id TEXT,
        id_donvi INTEGER DEFAULT 1
    )
    """)

    # ===== DANH MỤC METHOD =====
    query("""
    CREATE TABLE IF NOT EXISTS danh_muc_method (
        code_method TEXT PRIMARY KEY,
        name_method TEXT,
        path_method TEXT,
        parser_method TEXT,
        counter_method TEXT
    )
    """)

    # ===== MACHINE =====
    query("""
    CREATE TABLE IF NOT EXISTS machine (
        code_machine TEXT PRIMARY KEY,
        name_machine TEXT,
        serial_machine TEXT,
        location TEXT,
        note TEXT,
        counter_enabled INTEGER DEFAULT 1,
        ip_machine TEXT,
        path_machine TEXT,
        max_days INTEGER,
        times_per_day INTEGER,
        code_method TEXT,
        raw_data TEXT,
        code_don_vi TEXT
    )
    """)

    # ===== COUNTER LOG =====
    query("""
    CREATE TABLE IF NOT EXISTS counter_log (
        id_counter INTEGER PRIMARY KEY AUTOINCREMENT,
        code_machine TEXT,
        timestamp TEXT,
        total_counter INTEGER,
        bw_counter INTEGER,
        color_counter INTEGER,
        copy_counter INTEGER,
        printer_counter INTEGER,
        scan_counter INTEGER,
        raw_counter TEXT
    )
    """)

    print("✅ DB Initialized (NEW SCHEMA)")