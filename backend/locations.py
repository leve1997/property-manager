from backend.database_connection import get_db


def get_or_create_location(address):
    """Return existing location_id for this address, or create and return a new one."""
    with get_db() as conn:
        with conn:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO locations (address) VALUES (?)",
                (address,)
            )
        if cursor.lastrowid:
            return cursor.lastrowid
        row = conn.execute("SELECT id FROM locations WHERE address = ?", (address,)).fetchone()
        return row["id"]