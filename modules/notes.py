import os
import sys
import datetime

# Ensure root directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Directory to store notes and tasks
NOTES_DIR = os.path.join(os.path.dirname(__file__), "..", "notes")
os.makedirs(NOTES_DIR, exist_ok=True)

NOTES_FILE = os.path.join(NOTES_DIR, "saved_notes.txt")
TASKS_FILE = os.path.join(NOTES_DIR, "todo_list.txt")


def save_note(note_text: str) -> str:
    """Appends a timestamped note to saved_notes.txt."""
    if not note_text:
        return "Note content cannot be empty, boss."

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    entry = f"[{timestamp}] {note_text.strip()}\n"

    try:
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        return f"Got it, boss. Note saved: '{note_text.strip()}'"
    except Exception as e:
        return f"Failed to save note: {e}"


def read_notes() -> str:
    """Reads all saved notes."""
    if not os.path.exists(NOTES_FILE) or os.path.getsize(NOTES_FILE) == 0:
        return "You don't have any saved notes yet, boss."

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = f.readlines()

        output = "Here are your saved notes:\n" + "".join(notes[-5:])
        return output.strip()
    except Exception as e:
        return f"Failed to read notes: {e}"


def clear_all_notes() -> str:
    """Deletes all saved notes."""
    if not os.path.exists(NOTES_FILE) or os.path.getsize(NOTES_FILE) == 0:
        return "You have no saved notes to delete, boss."

    try:
        open(NOTES_FILE, "w", encoding="utf-8").close()
        return "All saved notes have been deleted, boss."
    except Exception as e:
        return f"Failed to delete notes: {e}"


def add_task(task_text: str) -> str:
    """Adds a task to the to-do list."""
    if not task_text:
        return "Task content cannot be empty, boss."

    try:
        with open(TASKS_FILE, "a", encoding="utf-8") as f:
            f.write(f"- [ ] {task_text.strip()}\n")
        return f"Added to your to-do list: '{task_text.strip()}'"
    except Exception as e:
        return f"Failed to add task: {e}"


def read_pending_tasks() -> str:
    """Reads and lists only the incomplete/pending tasks."""
    if not os.path.exists(TASKS_FILE) or os.path.getsize(TASKS_FILE) == 0:
        return "You have no tasks on your list, boss."

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            tasks = f.readlines()

        pending = [t.strip() for t in tasks if t.strip().startswith("- [ ]")]

        if not pending:
            return "You're all caught up! There are no pending tasks, boss."

        count = len(pending)
        formatted_list = "\n".join(pending)
        return f"You have {count} pending task{'s' if count > 1 else ''}:\n{formatted_list}"

    except Exception as e:
        return f"Failed to check pending tasks: {e}"


def mark_task_done(task_keyword: str) -> str:
    """Marks a task matching the keyword as completed ([x])."""
    if not os.path.exists(TASKS_FILE) or os.path.getsize(TASKS_FILE) == 0:
        return "Your to-do list is empty, boss."

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated = False
        new_lines = []
        for line in lines:
            if task_keyword.lower() in line.lower() and line.startswith("- [ ]"):
                new_lines.append(line.replace("- [ ]", "- [x]"))
                updated = True
            else:
                new_lines.append(line)

        if updated:
            with open(TASKS_FILE, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return f"Marked task matching '{task_keyword}' as completed!"
        else:
            return f"No pending task matching '{task_keyword}' was found, boss."

    except Exception as e:
        return f"Failed to update task: {e}"


def delete_task_by_keyword(keyword: str) -> str:
    """Deletes a specific task matching the keyword."""
    if not os.path.exists(TASKS_FILE) or os.path.getsize(TASKS_FILE) == 0:
        return "Your to-do list is already empty, boss."

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = [line for line in lines if keyword.lower() not in line.lower()]

        if len(new_lines) == len(lines):
            return f"No task matching '{keyword}' was found to delete, boss."

        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        return f"Successfully deleted task matching '{keyword}', boss."

    except Exception as e:
        return f"Failed to delete task: {e}"


def clear_tasks() -> str:
    """Clears the entire to-do list."""
    try:
        open(TASKS_FILE, "w", encoding="utf-8").close()
        return "Your to-do list has been cleared, boss."
    except Exception as e:
        return f"Failed to clear tasks: {e}"