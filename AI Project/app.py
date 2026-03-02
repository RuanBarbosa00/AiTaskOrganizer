from flask import Flask, request, jsonify, send_from_directory
import json, os
from datetime import datetime

# -----------------------------------------
# FLASK CONFIG
# -----------------------------------------

app = Flask(
    __name__,
    static_folder="interface",
    template_folder="interface"
)

TASKS_FILE = "tasks.json"
SETTINGS_FILE = "settings.json"

# -----------------------------------------
# HELPERS
# -----------------------------------------

def load_json(path, default):
    if not os.path.exists(path):
        return default
    return json.load(open(path, "r"))

def save_json(path, data):
    json.dump(data, open(path, "w"), indent=4)

# -----------------------------------------
# AI MODULES
# -----------------------------------------

from src.predict import classify_task
from src.date_extractor import extract_date
from src.status_engine import calculate_status
from src.priority_engine import priority_from_type_and_date

# -----------------------------------------
# FRONTEND ROUTES
# -----------------------------------------

@app.route("/")
def index():
    return send_from_directory("interface", "index.html")

@app.route("/tasks")
def tasks_page():
    return send_from_directory("interface", "tasks.html")

@app.route("/settings")
def settings_page():
    return send_from_directory("interface", "settings.html")

@app.route("/image_import")
def image_import_page():
    return send_from_directory("interface", "image_import.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("interface", path)

# -----------------------------------------
# API: TASKS
# -----------------------------------------

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(load_json(TASKS_FILE, []))


@app.route("/api/tasks", methods=["POST"])
def add_task():
    tasks = load_json(TASKS_FILE, [])
    data = request.json

    raw_text = data.get("name", "")

    # CLASSIFY
    task_type = classify_task(raw_text)

    # DATE
    due_dt = extract_date(raw_text)
    due_str = due_dt.strftime("%Y-%m-%d") if due_dt else ""

    # STATUS
    status = calculate_status(due_dt.date() if due_dt else None)

    # PRIORITY
    priority = priority_from_type_and_date(task_type, due_dt)

    task = {
        "name": raw_text,
        "type": task_type,
        "due": due_str,
        "priority": priority,
        "status": status
    }

    tasks.append(task)
    save_json(TASKS_FILE, tasks)

    return jsonify({"status": "ok", "task": task})


@app.route("/api/tasks/<int:index>", methods=["PUT"])
def update_task(index):
    tasks = load_json(TASKS_FILE, [])
    data = request.json

    raw_text = data.get("name", "")
    task_type = data.get("type", classify_task(raw_text))

    due_dt = extract_date(raw_text) if raw_text else None
    due_str = due_dt.strftime("%Y-%m-%d") if due_dt else data.get("due", "")

    status = calculate_status(due_dt.date() if due_dt else None)
    priority = priority_from_type_and_date(task_type, due_dt)

    updated = {
        "name": raw_text,
        "type": task_type,
        "due": due_str,
        "priority": priority,
        "status": status
    }

    tasks[index] = updated
    save_json(TASKS_FILE, tasks)

    return jsonify({"status": "ok", "task": updated})


@app.route("/api/tasks/<int:index>", methods=["DELETE"])
def delete_task(index):
    tasks = load_json(TASKS_FILE, [])
    tasks.pop(index)
    save_json(TASKS_FILE, tasks)
    return jsonify({"status": "ok"})

# -----------------------------------------
# API: SETTINGS
# -----------------------------------------

@app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify(load_json(SETTINGS_FILE, {}))


@app.route("/api/settings", methods=["POST"])
def save_settings():
    save_json(SETTINGS_FILE, request.json)
    return jsonify({"status": "ok"})

# -----------------------------------------
# API: DASHBOARD
# -----------------------------------------

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    tasks = load_json(TASKS_FILE, [])

    stats = {
        "total": len(tasks),
        "critical": sum(t["priority"] == "Critical" for t in tasks),
        "high": sum(t["priority"] == "High" for t in tasks),
        "upcoming": sum(t["status"] in ["COMING UP", "DUE TOMORROW"] for t in tasks),
        "overdue": sum(t["status"] == "OVERDUE" for t in tasks)
    }

    return jsonify(stats)

# -----------------------------------------
# API: IMAGE IMPORT (PREVIEW)
# -----------------------------------------

@app.route("/api/upload_image_preview", methods=["POST"])
def upload_image_preview():
    try:
        file = request.files["file"]
        path = "uploaded_image.png"
        file.save(path)

        from src.image_reader import extract_tasks_from_image
        raw_tasks = extract_tasks_from_image(path)

        if raw_tasks is None:
            raw_tasks = []

        preview = []
        for t in raw_tasks:
            if not isinstance(t, dict):
                continue

            name = t.get("name", "")
            task_type = t.get("type", "unknown")
            due_str = t.get("due", "")

            preview.append({
                "name": name,
                "type": task_type,
                "due": due_str
            })

        return jsonify(preview), 200

    except Exception as e:
        print("\n🔥 ERROR IN upload_image_preview:", e, "\n")
        return jsonify({"error": str(e)}), 500

# -----------------------------------------
# API: IMAGE IMPORT (CONFIRM)
# -----------------------------------------

@app.route("/api/confirm_image_tasks", methods=["POST"])
def confirm_image_tasks():
    tasks = load_json(TASKS_FILE, [])
    new_tasks = request.json

    tasks.extend(new_tasks)
    save_json(TASKS_FILE, tasks)

    return jsonify({"status": "ok", "added": len(new_tasks)})

# -----------------------------------------
# RUN
# -----------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
