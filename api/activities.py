from flask import Blueprint, request, jsonify
from backend.activities import create_activity, get_all_activities, search_activities

activities_bp = Blueprint('activities', __name__, url_prefix='/activities')

@activities_bp.route("/", methods=["GET", "POST"])
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


@activities_bp.route("/search", methods=["GET"])
def search_activities():
    manager = request.args.get("manager", "")
    building = request.args.get("building", "")
    date = request.args.get("date", "")

    activities_list = search_activities(
        manager=manager if manager else None,
        building=building if building else None,
        date=date if date else None
    )
    return jsonify(activities_list)
