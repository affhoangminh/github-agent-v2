import sqlite3

DB_PATH = "data/agent.db"

def connect():
    return sqlite3.connect(DB_PATH)

def query(sql, params=(), fetch=False):
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, params)

    if fetch:
        data = cur.fetchall()
        conn.close()
        return data

    conn.commit()
    conn.close()