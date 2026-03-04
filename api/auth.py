import logging
from flask import Blueprint, request, redirect, url_for, session, flash
from backend.auth import verify_user

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("Username and password required.", "error")
        return redirect(url_for("activities.index"))

    verified_username = verify_user(username, password)
    if verified_username:
        session["username"] = verified_username
        logger.info("User '%s' logged in", verified_username)
        return redirect(url_for("activities.index"))

    logger.warning("Failed login attempt for username '%s'", username)
    flash("Invalid username or password.", "error")
    return redirect(url_for("activities.index"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    username = session.get("username", "unknown")
    session.clear()
    logger.info("User '%s' logged out", username)
    return redirect(url_for("activities.index"))

