import sqlite3

DB_PATH = "data/agent.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 🔥 QUAN TRỌNG
    return conn


def query(sql, params=(), fetch=False):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, params)

        if fetch:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]  # 🔥 convert dict

        conn.commit()
        return True

    except Exception as e:
        print("❌ DB ERROR:", e)
        return None

    finally:
        conn.close()