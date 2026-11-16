import json
import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def get_conn():
    # Compose injects DATABASE_URL; service name "db" acts as hostname
    import psycopg2
    db_url = os.getenv("DATABASE_URL", "postgresql://labuser:labpass@localhost:5432/labdb")
    return psycopg2.connect(db_url)


@app.route("/")
def home():
    user_agent = request.headers.get("User-Agent", "").lower()
    if request.args.get("format") == "json" or "curl" in user_agent:
        return jsonify(
            message="Hello from a containerized Flask app!",
            environment=os.getenv("APP_ENV", "development"),
        )
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="healthy", service="flask-demo"), 200


@app.route("/init")
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS visits ("
        "id SERIAL PRIMARY KEY, "
        "ts TIMESTAMP DEFAULT NOW()"
        ");"
    )
    conn.commit()
    cur.close()
    conn.close()
    return "database initialized"


@app.route("/count")
def count():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO visits (ts) VALUES (NOW()); "
        "SELECT COUNT(*) FROM visits;"
    )
    n = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(total_visits=n)


@app.route("/api/student", methods=["GET", "POST"])
@app.route("/api/students", methods=["GET", "POST"])
def manage_students():
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not data:
            data = request.form.to_dict()

        if not data or not data.get("name"):
            return jsonify(error="No student data provided"), 400

        with open("students.txt", "a") as f:
            f.write(json.dumps(data) + "\n")

        return jsonify(message="Student saved successfully", data=data), 201

    if request.args.get("format") == "json":
        students = []
        if os.path.exists("students.txt"):
            with open("students.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        students.append(json.loads(line))
        return jsonify(students=students)

    return render_template("student_form.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
