from flask import Blueprint, render_template, jsonify

main_routes = Blueprint('main', __name__)

@main_routes.route("/")
def index():
    return render_template("index.html")

@main_routes.route("/apply")
def apply():
    return jsonify({"message": "Welcome to the application page!"})

@main_routes.route("/<path:path>")
def not_exist(path):
    return render_template("error404.html"), 404