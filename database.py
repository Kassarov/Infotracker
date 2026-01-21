import sqlite3

DB_FILE = "data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tracked (
        url TEXT PRIMARY KEY,
        platform TEXT,
        last_data TEXT
    )''')
    conn.commit()
    conn.close()

def get_last_data(url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT last_data FROM tracked WHERE url = ?", (url,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_last_data(url, platform, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO tracked (url, platform, last_data) VALUES (?, ?, ?)",
              (url, platform, data))
    conn.commit()
    conn.close()
