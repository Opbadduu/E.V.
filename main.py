import sys
from core.speaker import speak
from core.listener import listen
from modules.os_control import open_app, set_volume, lock_system
from modules.system_stats import get_battery_status, get_system_stats
from modules.web_tools import search_google, play_youtube, open_website

def process_command(command: str):
    if not command:
        return

    print(f"\n⚡ Processing command: '{command}'")

    # --- 1. Web & Online Tools ---
    if "youtube" in command or "play" in command:
        response = play_youtube(command)
        speak(response)

    elif "search" in command or "google" in command:
        response = search_google(command)
        speak(response)

    elif "website" in command or "dot com" in command or ".com" in command:
        response = open_website(command)
        speak(response)

    # --- 2. App Launching Commands ---
    elif "open" in command or "launch" in command:
        for keyword in ["open", "launch"]:
            if keyword in command:
                app_name = command.split(keyword)[-1].strip()
                response = open_app(app_name)
                speak(response)
                break

    # --- 3. System Stats & Battery ---
    elif "battery" in command or "power" in command:
        status = get_battery_status()
        speak(status)

    elif "stats" in command or "cpu" in command or "ram" in command:
        stats = get_system_stats()
        speak(stats)

    # --- 4. Volume Control ---
    elif "volume" in command or "mute" in command:
        response = set_volume(command)
        speak(response)

    # --- 5. Lock Laptop ---
    elif "lock" in command:
        speak(lock_system())

    # --- 6. Exit / Shutdown Assistant ---
    elif "exit" in command or "stop" in command or "bye" in command or "quit" in command:
        speak("Shutting down E.V. systems. Goodbye!")
        sys.exit()

    else:
        speak("Command not recognized in local modules yet.")

def main():
    speak("E.V. Virtual Assistant online. Give me a command!")
    
    while True:
        command = listen()
        process_command(command)

if __name__ == "__main__":
    main()