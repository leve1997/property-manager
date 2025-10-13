from flask import Blueprint, request, jsonify
from backend.database_connection import verify_user, get_all_activities, create_activity, search_activities as db_search_activities

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route("/login", methods=["POST", "OPTIONS"])
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


@api_bp.route("/check-auth", methods=["GET"])
def check_auth():
    # Always return logged in for MVP (no session)
    return jsonify({"logged_in": True, "username": "admin"})


@api_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"success": True})


@api_bp.route("/activities", methods=["GET", "POST"])
def activities():
    if request.method == "POST":
        data = request.json or {}
        required_fields = ["manager", "building", "date", "time", "description"]
        if not all(data.get(field) for field in required_fields):
            return jsonify({"error": "All fields are required"}), 400

        activity_id = create_activity(
            data["manager"],
            data["building"],
            data["date"],
            data["time"],
            data["description"]
        )
        return jsonify({"success": True, "id": activity_id})

    activities_list = get_all_activities()
    return jsonify(activities_list)


@api_bp.route("/activities/search", methods=["GET"])
def search_activities():
    manager = request.args.get("manager", "")
    building = request.args.get("building", "")
    date = request.args.get("date", "")

    activities_list = db_search_activities(
        manager=manager if manager else None,
        building=building if building else None,
        date=date if date else None
    )
    return jsonify(activities_list)
