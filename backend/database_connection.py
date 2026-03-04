import sqlite3
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_default_db_path = os.path.join(BASE_DIR, "backend", "database.db")
DB_PATH = os.getenv("DB_PATH", _default_db_path)


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
    except Exception:
        logger.exception("Unhandled exception during database operation")
        raise
    finally:
        conn.close()