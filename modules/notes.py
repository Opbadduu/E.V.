import os
import json
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "workspace.json")

def _load_data() -> dict:
    """Loads workspace data from JSON file."""
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        default_data = {"tasks": [], "notes": []}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4)
        return default_data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"tasks": [], "notes": []}


def _save_data(data: dict) -> None:
    """Saves workspace data to JSON file."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def add_task(title: str, due_time: str = "") -> str:
    """Adds a task with optional due time."""
    if not title:
        return "Task title cannot be empty, boss."

    data = _load_data()
    task_id = len(data["tasks"]) + 1
    new_task = {
        "id": task_id,
        "title": title.strip(),
        "status": "pending",
        "time": due_time.strip() if due_time else "Unspecified",
        "created_at": datetime.now().strftime("%Y-%m-%d %I:%M %p")
    }
    data["tasks"].append(new_task)
    _save_data(data)

    msg = f"Added task #{task_id}: '{title.strip()}'"
    if due_time:
        msg += f" for {due_time.strip()}"
    return msg + "."


def get_pending_tasks() -> str:
    """Retrieves all pending tasks."""
    data = _load_data()
    pending = [t for t in data["tasks"] if t["status"] == "pending"]

    if not pending:
        return "You have no pending tasks, boss."

    lines = [f"You have {len(pending)} pending task(s):"]
    for t in pending:
        time_info = f" (Scheduled: {t['time']})" if t['time'] != "Unspecified" else ""
        lines.append(f"• #{t['id']}: {t['title']}{time_info}")

    return "\n".join(lines)


def complete_task(identifier: str) -> str:
    """Marks a task as completed by ID or matching title."""
    data = _load_data()
    updated = False

    for t in data["tasks"]:
        if str(t["id"]) == str(identifier) or identifier.lower() in t["title"].lower():
            if t["status"] == "pending":
                t["status"] = "completed"
                updated = True
                break

    if updated:
        _save_data(data)
        return f"Marked task matching '{identifier}' as completed!"
    return f"No pending task matching '{identifier}' was found, boss."


def clear_all_tasks() -> str:
    """Clears all tasks."""
    data = _load_data()
    data["tasks"] = []
    _save_data(data)
    return "All tasks have been cleared from your database, boss."


def save_note(content: str) -> str:
    """Saves a timestamped note."""
    if not content:
        return "Note content cannot be empty, boss."

    data = _load_data()
    note_id = len(data["notes"]) + 1
    new_note = {
        "id": note_id,
        "content": content.strip(),
        "created_at": datetime.now().strftime("%Y-%m-%d %I:%M %p")
    }
    data["notes"].append(new_note)
    _save_data(data)
    return f"Note #{note_id} saved: '{content.strip()}'"


def get_notes() -> str:
    """Retrieves all saved notes."""
    data = _load_data()
    if not data["notes"]:
        return "You don't have any saved notes yet, boss."

    lines = ["Here are your saved notes:"]
    for n in data["notes"][-5:]:  # Last 5 notes
        lines.append(f"• [{n['created_at']}] #{n['id']}: {n['content']}")
    return "\n".join(lines)