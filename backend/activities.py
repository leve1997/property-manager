from backend.database_connection import get_db


def get_activities(filter_address=None, filter_date_from=None, filter_date_to=None,
                   filter_usernames=None, page=1, per_page=20):
    """Fetch paginated activities with optional filters. Returns (rows, total_count)."""

    base_query = """
        FROM property_activities pa
        JOIN locations l ON pa.location_id = l.id
        JOIN users u ON pa.user_id = u.id
        WHERE 1=1
    """
    params = []

    if filter_address:
        base_query += " AND l.address LIKE ?"
        params.append(f"%{filter_address}%")
    if filter_date_from:
        base_query += " AND DATE(pa.activity_date) >= ?"
        params.append(filter_date_from)
    if filter_date_to:
        base_query += " AND DATE(pa.activity_date) <= ?"
        params.append(filter_date_to)
    if filter_usernames:
        placeholders = ",".join("?" * len(filter_usernames))
        base_query += f" AND u.username IN ({placeholders})"
        params.extend(filter_usernames)

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) {base_query}", params)
        total = cursor.fetchone()[0]

        offset = (page - 1) * per_page
        cursor.execute(
            f"""
            SELECT pa.id, pa.activity_date, pa.note, l.address, u.username
            {base_query}
            ORDER BY pa.activity_date DESC
            LIMIT ? OFFSET ?
            """,
            params + [per_page, offset]
        )
        rows = cursor.fetchall()

    return [
        {
            "id": row["id"],
            "activity_date": row["activity_date"],
            "note": row["note"],
            "address": row["address"],
            "username": row["username"],
        }
        for row in rows
    ], total


def create_activity(location_id, user_id, note):
    """Insert a new activity and return its ID."""
    with get_db() as conn:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO property_activities (location_id, user_id, activity_date, note) VALUES (?, ?, CURRENT_TIMESTAMP, ?)",
                (location_id, user_id, note)
            )
        return cursor.lastrowid


def delete_activity(activity_id):
    """Delete an activity by ID. Returns True if deleted, False if not found."""
    with get_db() as conn:
        with conn:
            cursor = conn.execute("DELETE FROM property_activities WHERE id = ?", (activity_id,))
        return cursor.rowcount > 0