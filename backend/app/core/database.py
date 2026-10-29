import sqlite3
from pathlib import Path
from typing import Generator
from app.core.config import BASE_DIR

DB_PATH = BASE_DIR / "noticias_cepea.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
