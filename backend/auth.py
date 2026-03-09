from backend.database_connection import get_db
import bcrypt

def get_all_usernames():
    """Return a list of all usernames sorted alphabetically."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users ORDER BY username")
        return [row["username"] for row in cursor.fetchall()]


def verify_user(username, password):
    """Verify user credentials and return (username, user_id) if valid, None otherwise."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

    if row and bcrypt.checkpw(password.encode("utf-8"), row["password_hash"]):
        return username, row["id"]
    return None