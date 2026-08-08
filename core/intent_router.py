import json
import os
import sys
from groq import Groq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import GROQ_API_KEY
from modules.notes import (
    add_task,
    get_pending_tasks,
    complete_task,
    clear_all_tasks,
    save_note,
    get_notes
)

SYSTEM_PROMPT = """
You are E.V.'s Intent Router. Analyze the user query and classify it into a structured JSON action.

Output ONLY valid JSON with this exact structure (no markdown, no conversation):
{
  "action": "<ACTION_NAME>",
  "params": {
      "title": "<task or note text>",
      "time": "<scheduled time if specified, else empty string>",
      "identifier": "<task id or search keyword for deletion/completion>"
  }
}

Valid Action Names:
- "ADD_TASK": User wants to add a task, reminder, or to-do item.
- "GET_TASKS": User asks to view, check, or list pending tasks or to-do items.
- "COMPLETE_TASK": User marks a task done, finished, or complete.
- "CLEAR_TASKS": User asks to clear, wipe, or delete all tasks.
- "SAVE_NOTE": User wants to write down, save, or record a note.
- "GET_NOTES": User wants to read or view saved notes.
- "GENERAL": Use this for open conversation, questions, or non-task commands.
"""

def parse_and_execute(user_query: str) -> str | None:
    """
    Uses LLM to classify user intent into a JSON command, then executes the corresponding module.
    Returns the module execution message, or None if the query is a general AI query.
    """
    if not GROQ_API_KEY:
        return None

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0
        )

        raw_json = response.choices[0].message.content.strip()
        data = json.loads(raw_json)

        action = data.get("action")
        params = data.get("params", {})

        if action == "ADD_TASK":
            return add_task(params.get("title", ""), params.get("time", ""))

        elif action == "GET_TASKS":
            return get_pending_tasks()

        elif action == "COMPLETE_TASK":
            return complete_task(params.get("identifier", ""))

        elif action == "CLEAR_TASKS":
            return clear_all_tasks()

        elif action == "SAVE_NOTE":
            return save_note(params.get("title", ""))

        elif action == "GET_NOTES":
            return get_notes()

        # Fallback to general conversation / OS commands
        return None

    except Exception:
        return None