from backend.database_connection import get_db


def get_or_create_location(address):
    """Return existing location_id for this address, or create and return a new one."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM locations WHERE address = ?", (address,))
        row = cursor.fetchone()

        if row:
            return row["id"]

        with conn:
            cursor.execute(
                "INSERT INTO locations (address) VALUES (?)",
                (address,)
            )
        return cursor.lastrowid