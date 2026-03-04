from backend.database_connection import get_db

def get_all_activities():
    """Fetch all activities ordered by date and time descending."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activities ORDER BY date DESC, time DESC")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "manager": row["manager"],
            "building": row["building"],
            "date": row["date"],
            "time": row["time"],
            "description": row["description"],
        }
        for row in rows
    ]


def create_activity(manager, building, date, time, description):
    """Create a new activity and return its ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO activities (manager, building, date, time, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        (manager, building, date, time, description),
    )
    conn.commit()
    activity_id = cursor.lastrowid
    conn.close()
    return activity_id


def search_activities(manager=None, building=None, date=None):
    """Search activities with optional filters."""
    query = "SELECT * FROM activities WHERE 1 = 1"
    params = []

    if manager:
        query += " AND manager LIKE ?"
        params.append(f"%{manager}%")
    if building:
        query += " AND building LIKE ?"
        params.append(f"%{building}%")
    if date:
        query += " AND date = ?"
        params.append(date)

    query += " ORDER BY date DESC, time DESC"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "manager": row["manager"],
            "building": row["building"],
            "date": row["date"],
            "time": row["time"],
            "description": row["description"],
        }
        for row in rows
    ]