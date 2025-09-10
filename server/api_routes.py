from flask import Blueprint, jsonify, request

api_routes = Blueprint('api', __name__)

@api_routes.route("/free-slots")
def get_slots():
    slots = [
        {"id": 1, "time": "10:00 AM"},
        {"id": 2, "time": "11:00 AM"},
        {"id": 3, "time": "12:00 PM"},
    ]
    return jsonify(slots)

@api_routes.route("/<path:invalid_path>")
def api_not_found(invalid_path):
    return jsonify({
        "error": "Invalid API endpoint",
        "path": f"/api/{invalid_path}"
    }), 404