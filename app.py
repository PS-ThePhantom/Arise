from flask import Flask, jsonify, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route("/")
def index():
    return render_template("index.html")


#Handle all non-existent routes with a 404 error.
@app.route("/<path:path>")
def not_exist(path):
    return jsonify({'error': 'Not Found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)