import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/app/data/boda.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT,
            alias TEXT,
            table_name TEXT,
            group_name TEXT,
            code TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            mission_type TEXT NOT NULL DEFAULT 'foto',
            base_points INTEGER NOT NULL DEFAULT 3,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS guest_missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id INTEGER NOT NULL,
            mission_id INTEGER NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            completed_at TEXT,
            FOREIGN KEY (guest_id) REFERENCES guests(id),
            FOREIGN KEY (mission_id) REFERENCES missions(id)
        );

        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id INTEGER NOT NULL,
            mission_id INTEGER,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            mime_type TEXT,
            size_bytes INTEGER,
            comment TEXT,
            points INTEGER NOT NULL DEFAULT 0,
            favorite INTEGER NOT NULL DEFAULT 0,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (guest_id) REFERENCES guests(id),
            FOREIGN KEY (mission_id) REFERENCES missions(id)
        );
        """)


def stats():
    with get_conn() as conn:
        guests = conn.execute("SELECT COUNT(*) AS n FROM guests").fetchone()["n"]
        missions = conn.execute("SELECT COUNT(*) AS n FROM missions").fetchone()["n"]
        uploads = conn.execute("SELECT COUNT(*) AS n FROM uploads").fetchone()["n"]
        completed = conn.execute("SELECT COUNT(*) AS n FROM guest_missions WHERE completed = 1").fetchone()["n"]

    return {
        "guests": guests,
        "missions": missions,
        "uploads": uploads,
        "completed": completed,
        "now": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
