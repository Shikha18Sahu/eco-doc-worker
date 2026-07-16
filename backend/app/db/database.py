import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "workflow.db")
DB_PATH = os.path.abspath(DB_PATH)


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflows (
            workflow_id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            status TEXT NOT NULL,
            next_action TEXT,
            confidence REAL,
            human_review_required INTEGER,
            structured_data TEXT,
            validation_errors TEXT,
            state_json TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()