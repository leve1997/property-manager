from backend.database_connection import get_db


def get_or_create_location(address):
    """Return existing location_id for this address, or create and return a new one."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM locations WHERE address = ?", (address,))
    row = cursor.fetchone()

    if row:
        conn.close()
        return row["id"]

    cursor.execute(
        "INSERT INTO locations (address) VALUES (?)",
        (address,)
    )
    conn.commit()
    location_id = cursor.lastrowid
    conn.close()
    return location_id