import sqlite3

DB_PATH = "data/agent.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def query(sql, params=(), fetch=False):
    """
    query dùng chung cho toàn hệ thống

    fetch=True  → trả dữ liệu
    fetch=False → commit
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, params)

        if fetch:
            rows = cursor.fetchall()
            return rows

        conn.commit()
        return True

    except Exception as e:
        print("❌ DB ERROR:", e)
        return None

    finally:
        conn.close()