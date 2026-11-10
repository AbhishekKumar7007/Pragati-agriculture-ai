import os
import sqlite3
from datetime import date

DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pragati.db")


def init_passport_db(db_path=DEFAULT_DB):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crop_health_passport (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                crop_name TEXT NOT NULL,
                growth_stage TEXT NOT NULL,
                observation TEXT NOT NULL,
                log_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_crop_passport_entry(crop_name, growth_stage, observation, log_date=None, db_path=DEFAULT_DB, user_id=None):
    crop_name = (crop_name or "").strip()
    growth_stage = (growth_stage or "").strip()
    observation = (observation or "").strip()
    if not crop_name or not growth_stage or not observation:
        raise ValueError("Crop name, growth stage, and observation are required.")
    if log_date is None:
        log_date = date.today().isoformat()
    try:
        date.fromisoformat(log_date)
    except (TypeError, ValueError):
        raise ValueError("Date must use YYYY-MM-DD format.")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("""
            INSERT INTO crop_health_passport
            (user_id, crop_name, growth_stage, observation, log_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, crop_name, growth_stage, observation, log_date))
        return cursor.lastrowid


def get_crop_history(crop_name=None, db_path=DEFAULT_DB, user_id=None):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        if crop_name and crop_name.strip():
            rows = conn.execute("""
                SELECT id, crop_name, growth_stage, observation, log_date, created_at
                FROM crop_health_passport
                WHERE crop_name LIKE ? AND (? IS NULL OR user_id = ?)
                ORDER BY log_date DESC, id DESC
            """, (f"%{crop_name.strip()}%", user_id, user_id)).fetchall()
        else:
            rows = conn.execute("""
                SELECT id, crop_name, growth_stage, observation, log_date, created_at
                FROM crop_health_passport
                WHERE (? IS NULL OR user_id = ?)
                ORDER BY log_date DESC, id DESC
            """, (user_id, user_id)).fetchall()
    return [dict(row) for row in rows]
