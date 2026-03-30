from database.db import query


# ================= INIT DATABASE =================
def init_db():
    # ===== ORGANIZATION =====
    query("""
    CREATE TABLE IF NOT EXISTS organization (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license TEXT,
        org_code TEXT,
        name TEXT,
        address TEXT,
        contact_name TEXT,
        contact_phone TEXT
    )
    """)

    # ===== DATA METHOD (QUAN TRỌNG) =====
    query("""
    CREATE TABLE IF NOT EXISTS data_method (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        name TEXT,
        data_url TEXT,
        raw_type TEXT,
        parser TEXT
    )
    """)

    # ===== MACHINE =====
    query("""
    CREATE TABLE IF NOT EXISTS machine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id INTEGER,
        machine_code TEXT UNIQUE,
        name TEXT,
        serial TEXT,
        storage_code TEXT,
        max_days INTEGER,
        times_per_day INTEGER,
        note TEXT,

        location TEXT,
        method_code TEXT,
        data_url TEXT,
        raw_data TEXT
    )
    """)

    # ===== COUNTER LOG =====
    query("""
    CREATE TABLE IF NOT EXISTS counter_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id INTEGER,
        timestamp TEXT,
        total INTEGER,
        bw INTEGER,
        color INTEGER,
        copy INTEGER,
        printer INTEGER,
        scan INTEGER,
        raw TEXT
    )
    """)

    print("✅ DB Initialized")


# ================= SEED DATA =================
def seed_data():
    # tránh insert trùng
    exists = query("SELECT * FROM data_method LIMIT 1", fetch=True)
    if exists:
        return

    # ===== DATA METHOD =====
    query("""
    INSERT INTO data_method (code, name, data_url, raw_type, parser)
    VALUES
    ('R001', 'Ricoh IM Series', '/web/guest/en/websys/status/getUnificationCounter.cgi', 'HTML'),
    ('R002', 'Ricoh Counter Page', '/web/guest/en/websys/webArch/mainFrame.cgi', 'HTML'),
    ('T001', 'Toshiba E Series', '/Counters/Counter.html', 'HTML', 'toshiba_parser')
    """)

    # ===== ORGANIZATION DEMO =====
    query("""
    INSERT INTO organization (
        license, org_code, name, address, contact_name, contact_phone
    )
    VALUES (
        'LIC001',
        'ORG001',
        'Công ty Demo',
        'Thái Nguyên',
        'Admin',
        '0123456789'
    )
    """)

    print("✅ Seeded data_method & organization")