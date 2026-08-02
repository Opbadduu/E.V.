import sys
from core.speaker import speak
from core.listener import listen
from modules.os_control import open_app, set_volume, lock_system
from modules.system_stats import get_battery_status, get_system_stats

def process_command(command: str):
    if not command:
        return

    print(f"\n⚡ Processing command: '{command}'")

    # --- 1. App Launching Commands ---
    if "open" in command or "launch" in command:
        # Extract app name after "open" or "launch"
        for keyword in ["open", "launch"]:
            if keyword in command:
                app_name = command.split(keyword)[-1].strip()
                response = open_app(app_name)
                speak(response)
                break

    # --- 2. System Stats & Battery ---
    elif "battery" in command or "power" in command:
        status = get_battery_status()
        speak(status)

    elif "stats" in command or "cpu" in command or "ram" in command or "system status" in command:
        stats = get_system_stats()
        speak(stats)

    # --- 3. Volume Control ---
    elif "volume" in command or "mute" in command:
        response = set_volume(command)
        speak(response)

    # --- 4. Lock Laptop ---
    elif "lock" in command:
        speak(lock_system())

    # --- 5. Exit / Shutdown Assistant ---
    elif "exit" in command or "stop" in command or "bye" in command or "quit" in command:
        speak("Shutting down E.V. systems. Goodbye!")
        sys.exit()

    else:
        speak("Command not recognized in system tools yet. We can route this to Gemini once brain.py is ready!")

def main():
    speak("E.V. Virtual Assistant online. Give me a command!")
    
    while True:
        # Takes input (currently text input until mic issue is resolved)
        command = listen()
        process_command(command)

if __name__ == "__main__":
    main()