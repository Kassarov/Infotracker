import sqlite3, json
DB = "data.db"

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS tracked
                       (url TEXT PRIMARY KEY,
                        platform TEXT,
                        last_data TEXT)""")

def get_last_data(url: str) -> str | None:
    with sqlite3.connect(DB) as con:
        cur = con.execute("SELECT last_data FROM tracked WHERE url=?", (url,))
        return cur.fetchone()[0] if cur.fetchone() else None

def set_last_data(url: str, platform: str, data: str):
    with sqlite3.connect(DB) as con:
        con.execute("INSERT OR REPLACE INTO tracked(url,platform,last_data) VALUES (?,?,?)",
                    (url, platform, data))
