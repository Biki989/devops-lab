import os
import json
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    user_agent = request.headers.get("User-Agent", "").lower()
    if request.args.get("format") == "json" or "curl" in user_agent:
        return jsonify(
            message="Hello from a containerized Flask app!",
            environment=os.getenv("APP_ENV", "development"),
        )
    return render_template("index.html")


@app.route("/api/student", methods=["POST"])
def add_student():
    data = request.get_json()
    if not data:
        data = request.form.to_dict()

    if not data:
        return jsonify(error="No student data provided"), 400

    with open("students.txt", "a") as f:
        f.write(json.dumps(data) + "\n")

    return jsonify(message="Student saved successfully", data=data), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
