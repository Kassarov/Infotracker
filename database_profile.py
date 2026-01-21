import sqlite3, json

DB = "data.db"

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS posts (
            post_id TEXT PRIMARY KEY,
            platform TEXT,
            url TEXT,
            likes INTEGER,
            views INTEGER,
            comments TEXT,
            last_check TEXT
        )""")

def get_post(post_id: str):
    with sqlite3.connect(DB) as con:
        cur = con.execute("SELECT likes, views, comments FROM posts WHERE post_id=?", (post_id,))
        return cur.fetchone()

def save_post(post_id: str, platform: str, url: str, likes: int, views: int, comments: list):
    with sqlite3.connect(DB) as con:
        con.execute("""INSERT OR REPLACE INTO posts(post_id, platform, url, likes, views, comments, last_check)
                       VALUES (?,?,?,?,?,?, datetime('now'))""",
                    (post_id, platform, url, likes, views, json.dumps(comments, ensure_ascii=False)))
