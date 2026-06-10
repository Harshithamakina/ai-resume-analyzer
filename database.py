import sqlite3
import json
from datetime import datetime

DB = "history.db"

def init():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT,
            email     TEXT,
            score     INTEGER,
            label     TEXT,
            skills    TEXT,
            job_title TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save(name, email, score, label, skills, job_title=""):
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO history (name,email,score,label,skills,job_title,timestamp) VALUES (?,?,?,?,?,?,?)",
        (name, email, score, label, json.dumps(skills), job_title, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()

def get_all():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT name,email,score,label,job_title,timestamp FROM history ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return rows
