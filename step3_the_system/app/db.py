import os
import sqlite3

DEFAULT_DB_PATH = "appointments.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    attendees INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_email_date
    ON appointments (email, appointment_date);

CREATE INDEX IF NOT EXISTS idx_date
    ON appointments (appointment_date);
"""


def get_db_path() -> str:
    return os.environ.get("APPOINTMENTS_DB", DEFAULT_DB_PATH)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection | None = None) -> None:
    if conn is None:
        conn = get_connection()
        try:
            conn.executescript(SCHEMA)
            conn.commit()
        finally:
            conn.close()
    else:
        conn.executescript(SCHEMA)
        conn.commit()
