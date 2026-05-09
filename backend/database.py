import sqlite3

def get_db():
    conn = sqlite3.connect("meetings.db")
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            transcript TEXT,
            summary TEXT,
            action_items TEXT,
            email_draft TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
