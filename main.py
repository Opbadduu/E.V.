import sys
from core.speaker import speak
from core.listener import listen
from core.brain import ask_ai
from modules.os_control import open_app, set_volume, lock_system
from modules.system_stats import get_battery_status, get_system_stats
from modules.web_tools import search_google, play_youtube, open_website
from modules.notes import (
    save_note,
    read_notes,
    add_task,
    read_pending_tasks,
    mark_task_done,
    delete_task_by_keyword,
    clear_tasks,
)

def process_command(command: str):
    if not command:
        return

    print(f"\n⚡ Processing command: '{command}'")

    # --- 1. Notes & Task Management ---
    if "note down" in command or "save note" in command or "write note" in command:
        # Extract content after trigger
        content = command.replace("note down", "").replace("save note", "").replace("write note", "").strip()
        speak(save_note(content))

    elif "read my notes" in command or "show my notes" in command or "view notes" in command:
        speak(read_notes())

    elif "add task" in command or "remind me to" in command:
        content = command.replace("add task", "").replace("remind me to", "").strip()
        speak(add_task(content))

    elif "pending task" in command or "what are my tasks" in command or "show my tasks" in command or "to do list" in command:
        speak(read_pending_tasks())

    elif "mark done" in command or "task completed" in command:
        keyword = command.replace("mark done", "").replace("task completed", "").replace("mark", "").replace("done", "").strip()
        speak(mark_task_done(keyword))

    elif "delete task" in command or "remove task" in command:
        keyword = command.replace("delete task", "").replace("remove task", "").strip()
        speak(delete_task_by_keyword(keyword))

    elif "clear all tasks" in command or "clear my to do list" in command:
        speak(clear_tasks())

    # --- 2. Web & Online Tools ---
    elif "youtube" in command or "play" in command:
        response = play_youtube(command)
        speak(response)

    elif "search" in command or "google" in command:
        response = search_google(command)
        speak(response)

    elif "website" in command or "dot com" in command or ".com" in command:
        response = open_website(command)
        speak(response)

    # --- 3. App Launching Commands ---
    elif "open" in command or "launch" in command:
        for keyword in ["open", "launch"]:
            if keyword in command:
                app_name = command.split(keyword)[-1].strip()
                response = open_app(app_name)
                speak(response)
                break

    # --- 4. System Stats & Battery ---
    elif "battery" in command or "power" in command:
        status = get_battery_status()
        speak(status)

    elif "stats" in command or "cpu" in command or "ram" in command:
        stats = get_system_stats()
        speak(stats)

    # --- 5. Volume Control ---
    elif "volume" in command or "mute" in command:
        response = set_volume(command)
        speak(response)

    # --- 6. Lock Laptop ---
    elif "lock" in command:
        speak(lock_system())

    # --- 7. Exit / Shutdown Assistant ---
    elif "exit" in command or "stop" in command or "bye" in command or "quit" in command:
        speak("Shutting down E.V. systems. Goodbye!")
        sys.exit()

    # --- 8. Fallback to Groq AI Brain ---
    else:
        response = ask_ai(command)
        speak(response)

def main():
    speak("E.V. Virtual Assistant online. Give me a command!")

    # Startup Briefing: Announce pending tasks only when active tasks exist
    pending_briefing = read_pending_tasks()
    if pending_briefing.startswith("You have") and "no tasks" not in pending_briefing:
        speak("You have pending tasks on your list, boss.")

    while True:
        command = listen()
        process_command(command)

if __name__ == "__main__":
    main()