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


@app.route("/api/student", methods=["GET", "POST"])
@app.route("/api/students", methods=["GET", "POST"])
def manage_students():
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not data:
            data = request.form.to_dict()

        if not data:
            return jsonify(error="No student data provided"), 400

        with open("students.txt", "a") as f:
            f.write(json.dumps(data) + "\n")

        return jsonify(message="Student saved successfully", data=data), 201

    form_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Add Student</title>
        <style>
            body { font-family: sans-serif; background: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
            .card { background: #1e293b; padding: 2.5rem; border-radius: 12px; text-align: center; border: 1px solid #334155; }
            input { margin: 10px 0; padding: 10px; width: 80%; border-radius: 6px; border: none; }
            button { margin-top: 15px; padding: 10px 20px; cursor: pointer; background: #38bdf8; border: none; border-radius: 6px; color: #000; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Add Student</h2>
            <form method="POST" action="/api/students">
                <input type="text" name="name" placeholder="Student Name" required><br>
                <input type="number" name="age" placeholder="Student Age" required><br>
                <button type="submit">Save Student</button>
            </form>
        </div>
    </body>
    </html>
    """
    return form_html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
