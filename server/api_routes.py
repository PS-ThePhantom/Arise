from flask import Blueprint, jsonify, request
from .services.data_validity import month_year_free_slot
from .services.slots import available_slots

api_routes = Blueprint('api', __name__)

@api_routes.route("/free-slots")
def get_slots():
    month = request.args.get("month")
    year = request.args.get("year")

    error = month_year_free_slot(month, year)

    if error:
        return jsonify({"error": error}), 400
    
    month = int(month)
    year = int(year)

    slots = available_slots(month, year)

    return jsonify({"year": year, "month": month, "slots": slots}), 200

@api_routes.route("/<path:invalid_path>")
def api_not_found(invalid_path):
    return jsonify({
        "error": "Invalid API endpoint",
        "path": f"/api/{invalid_path}"
    }), 404