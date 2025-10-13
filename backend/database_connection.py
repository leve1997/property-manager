import sqlite3
import os
import bcrypt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def verify_user(username, password):
    """Verify user credentials and return username if valid, None otherwise."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and bcrypt.checkpw(password.encode("utf-8"), row["password_hash"]):
        return username
    return None


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