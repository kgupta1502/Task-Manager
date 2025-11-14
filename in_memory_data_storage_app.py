# in_memory_data_storage_app.py
# Place this file in: task-manager-backend/task-manager/server/app/

from flask import Blueprint, jsonify, request
from datetime import datetime, date
import re

tasks_bp = Blueprint("tasks_bp", __name__)

# In-memory stores (integers ids to match the style in your other modules)
_CATEGORIES = []
_TASKS = []
_next_cat_id = 1
_next_task_id = 1

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ALLOWED_PRIORITIES = {"low", "medium", "high"}


def _is_valid_date(s):
    if not isinstance(s, str) or not DATE_RE.match(s):
        return False
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def register_tasks(app):
    """Call this from your main app.py to register the endpoints."""
    app.register_blueprint(tasks_bp)


# Category endpoints
@tasks_bp.route("/api/categories", methods=["POST"])
def create_category():
    global _next_cat_id
    data = request.get_json() or {}
    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Category 'name' is required"}), 400
    cat = {"id": _next_cat_id, "name": name.strip(), "description": data.get("description", "")}
    _CATEGORIES.append(cat)
    _next_cat_id += 1
    return jsonify(cat), 201


@tasks_bp.route("/api/categories", methods=["GET"])
def list_categories():
    return jsonify({"categories": _CATEGORIES})


@tasks_bp.route("/api/categories/<int:cat_id>", methods=["GET"])
def get_category(cat_id):
    c = next((x for x in _CATEGORIES if x["id"] == cat_id), None)
    if not c:
        return jsonify({"error": "Category not found"}), 404
    return jsonify(c)


@tasks_bp.route("/api/categories/<int:cat_id>", methods=["PUT"])
def update_category(cat_id):
    data = request.get_json() or {}
    c = next((x for x in _CATEGORIES if x["id"] == cat_id), None)
    if not c:
        return jsonify({"error": "Category not found"}), 404
    if "name" in data:
        name = data.get("name")
        if not name or not isinstance(name, str) or not name.strip():
            return jsonify({"error": "name must be a non-empty string"}), 400
        c["name"] = name.strip()
    if "description" in data:
        c["description"] = data.get("description", "")
    return jsonify(c)


@tasks_bp.route("/api/categories/<int:cat_id>", methods=["DELETE"])
def delete_category(cat_id):
    global _TASKS
    c = next((x for x in _CATEGORIES if x["id"] == cat_id), None)
    if not c:
        return jsonify({"error": "Category not found"}), 404
    # dissociate tasks from this category
    for t in _TASKS:
        if t.get("category_id") == cat_id:
            t["category_id"] = None
    _CATEGORIES[:] = [x for x in _CATEGORIES if x["id"] != cat_id]
    return ("", 204)


# Task endpoints
@tasks_bp.route("/api/tasks", methods=["POST"])
def create_task():
    global _next_task_id
    data = request.get_json() or {}
    title = data.get("title")
    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is required"}), 400

    category_id = data.get("category_id")
    if category_id is not None:
        if not any(c["id"] == category_id for c in _CATEGORIES):
            return jsonify({"error": "category_id does not exist"}), 400

    due_date = data.get("due_date")
    if due_date is not None:
        if not _is_valid_date(due_date):
            return jsonify({"error": "due_date must be YYYY-MM-DD"}), 400

    priority = data.get("priority", "medium") or "medium"
    if priority not in ALLOWED_PRIORITIES:
        return jsonify({"error": f"priority must be one of {sorted(ALLOWED_PRIORITIES)}"}), 400

    task = {
        "id": _next_task_id,
        "title": title.strip(),
        "description": data.get("description", ""),
        "category_id": category_id,
        "due_date": due_date,
        "completed": bool(data.get("completed", False)),
        "priority": priority,
    }
    _TASKS.append(task)
    _next_task_id += 1
    return jsonify(task), 201


@tasks_bp.route("/api/tasks", methods=["GET"])
def list_tasks():
    # filters: category_id, overdue, completed
    args = request.args
    results = list(_TASKS)
    cat = args.get("category_id")
    if cat is not None:
        try:
            cid = int(cat)
        except ValueError:
            return jsonify({"error": "category_id must be integer"}), 400
        results = [t for t in results if t.get("category_id") == cid]

    if "completed" in args:
        val = args.get("completed").lower()
        if val in ("true", "1"):
            want = True
        elif val in ("false", "0"):
            want = False
        else:
            return jsonify({"error": "completed filter must be true/false"}), 400
        results = [t for t in results if bool(t.get("completed", False)) == want]

    if "overdue" in args:
        val = args.get("overdue").lower()
        if val in ("true", "1"):
            want = True
        elif val in ("false", "0"):
            want = False
        else:
            return jsonify({"error": "overdue filter must be true/false"}), 400
        today = date.today()
        def is_overdue(t):
            dd = t.get("due_date")
            if not dd:
                return False
            try:
                d = datetime.strptime(dd, "%Y-%m-%d").date()
            except ValueError:
                return False
            return (d < today) and (not t.get("completed", False))
        results = [t for t in results if is_overdue(t) == want]

    return jsonify({"tasks": results, "count": len(results)})


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    t = next((x for x in _TASKS if x["id"] == task_id), None)
    if not t:
        return jsonify({"error": "task not found"}), 404
    return jsonify(t)


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json() or {}
    t = next((x for x in _TASKS if x["id"] == task_id), None)
    if not t:
        return jsonify({"error": "task not found"}), 404

    if "title" in data:
        title = data.get("title")
        if not title or not isinstance(title, str) or not title.strip():
            return jsonify({"error": "title must be non-empty string"}), 400
        t["title"] = title.strip()

    if "description" in data:
        t["description"] = data.get("description", "")

    if "category_id" in data:
        cid = data.get("category_id")
        if cid is not None and not any(c["id"] == cid for c in _CATEGORIES):
            return jsonify({"error": "category_id does not exist"}), 400
        t["category_id"] = cid

    if "due_date" in data:
        dd = data.get("due_date")
        if dd is None:
            t["due_date"] = None
        else:
            if not _is_valid_date(dd):
                return jsonify({"error": "due_date must be YYYY-MM-DD or null"}), 400
            t["due_date"] = dd

    if "completed" in data:
        t["completed"] = bool(data.get("completed"))

    if "priority" in data:
        p = data.get("priority") or "medium"
        if p not in ALLOWED_PRIORITIES:
            return jsonify({"error": f"priority must be one of {sorted(ALLOWED_PRIORITIES)}"}), 400
        t["priority"] = p

    return jsonify(t)


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global _TASKS
    t = next((x for x in _TASKS if x["id"] == task_id), None)
    if not t:
        return jsonify({"error": "task not found"}), 404
    _TASKS = [x for x in _TASKS if x["id"] != task_id]
    return ("", 204)


# Overdue & stats
@tasks_bp.route("/api/tasks/overdue", methods=["GET"])
def overdue_tasks():
    today = date.today()
    out = []
    for t in _TASKS:
        dd = t.get("due_date")
        if not dd:
            continue
        try:
            d = datetime.strptime(dd, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d < today and not t.get("completed", False):
            out.append(t)
    return jsonify({"overdue_tasks": out, "count": len(out)})


@tasks_bp.route("/api/tasks/stats", methods=["GET"])
def tasks_stats():
    total = len(_TASKS)
    completed = sum(1 for t in _TASKS if t.get("completed", False))
    pending = total - completed
    today = date.today()
    overdue = 0
    for t in _TASKS:
        dd = t.get("due_date")
        if not dd:
            continue
        try:
            d = datetime.strptime(dd, "%Y-%m-%d").date()
        except ValueError:
            continue
        if (d < today) and (not t.get("completed", False)):
            overdue += 1
    return jsonify({
        "total_tasks": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue
    })
