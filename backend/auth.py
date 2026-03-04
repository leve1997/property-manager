from backend.database_connection import get_db
import bcrypt

def verify_user(username, password):
    """Verify user credentials and return username if valid, None otherwise."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

    if row and bcrypt.checkpw(password.encode("utf-8"), row["password_hash"]):
        return username
    return None