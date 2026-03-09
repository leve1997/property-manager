import logging
from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from backend.auth import verify_user

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route("/login", methods=["GET"])
def login():
    if session.get("username"):
        return redirect(url_for("activities.index"))
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash("Username and password required.", "error")
        return redirect(url_for("auth.login"))

    result = verify_user(username, password)
    if result:
        verified_username, user_id = result
        session["username"] = verified_username
        session["user_id"] = user_id
        logger.info("User '%s' logged in", verified_username)
        return redirect(url_for("activities.index"))

    logger.warning("Failed login attempt for username '%s'", username)
    flash("Invalid username or password.", "error")
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    username = session.get("username", "unknown")
    session.clear()
    logger.info("User '%s' logged out", username)
    return redirect(url_for("auth.login"))
