import sys
from core.speaker import speak
from core.listener import listen
from core.brain import ask_ai
from core.intent_router import parse_and_execute
from modules.os_control import open_app, set_volume, lock_system
from modules.system_stats import get_battery_status, get_system_stats
from modules.web_tools import search_google, play_youtube, open_website
from modules.notes import get_pending_tasks

def process_command(command: str) -> str | None:
    if not command:
        return None

    print(f"\n⚡ Processing command: '{command}'")

    # --- 1. LLM Intent Router (Handles Notes, Tasks, Reminders dynamically) ---
    intent_response = parse_and_execute(command)
    if intent_response:
        return intent_response

    cmd_lower = command.lower().strip()

    # --- 2. Web & Online Tools ---
    if "youtube" in cmd_lower or "play" in cmd_lower:
        return play_youtube(command)

    elif "search" in cmd_lower or "google" in cmd_lower:
        return search_google(command)

    elif "website" in cmd_lower or "dot com" in cmd_lower or ".com" in cmd_lower:
        return open_website(command)

    # --- 3. App Launching Commands ---
    elif "open" in cmd_lower or "launch" in cmd_lower:
        for keyword in ["open", "launch"]:
            if keyword in cmd_lower:
                app_name = command.split(keyword)[-1].strip()
                return open_app(app_name)

    # --- 4. System Stats & Battery ---
    elif "battery" in cmd_lower or "power" in cmd_lower:
        return get_battery_status()

    elif "stats" in cmd_lower or "cpu" in cmd_lower or "ram" in cmd_lower:
        return get_system_stats()

    # --- 5. Volume Control ---
    elif "volume" in cmd_lower or "mute" in cmd_lower:
        return set_volume(command)

    # --- 6. Lock Laptop ---
    elif "lock" in cmd_lower:
        return lock_system()

    # --- 7. Exit / Shutdown Assistant ---
    elif any(k in cmd_lower for k in ["exit", "stop", "bye", "quit"]):
        speak("Shutting down E.V. systems. Goodbye!")
        sys.exit()

    # --- 8. Fallback to Groq AI Brain ---
    else:
        return ask_ai(command)

def main():
    speak("hey boss , what's to build today? ")

    # Startup Briefing: Check pending tasks from workspace.json
    pending_briefing = get_pending_tasks()
    if pending_briefing.startswith("You have") and "no pending tasks" not in pending_briefing:
        speak("just a reminder: You have pending tasks on your list")

    while True:
        command = listen()
        response = process_command(command)
        if response:
            speak(response)

if __name__ == "__main__":
    main()