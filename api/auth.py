from flask import Blueprint, request, jsonify
from backend.auth import verify_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 204

    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    verified_username = verify_user(username, password)
    if verified_username:
        return jsonify({"success": True, "username": verified_username})

    return jsonify({"error": "Invalid username or password"}), 401


@auth_bp.route("/check-auth", methods=["GET"])
def check_auth():
    # Always return logged in for MVP (no session)
    return jsonify({"logged_in": True, "username": "admin"})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"success": True})

