import os
import subprocess
import pyautogui

def open_app(app_name: str) -> str:
    """
    Opens common desktop applications.
    """
    app_name = app_name.lower().strip()

    try:
        if "notepad" in app_name:
            subprocess.Popen(["notepad.exe"])
            return "Opening Notepad."

        elif "chrome" in app_name:
            os.system("start chrome")
            return "Opening Google Chrome."

        elif "calculator" in app_name or "calc" in app_name:
            subprocess.Popen(["calc.exe"])
            return "Opening Calculator."

        elif "cmd" in app_name or "terminal" in app_name or "command prompt" in app_name:
            os.system("start cmd")
            return "Opening Command Prompt."

        elif "explorer" in app_name or "file manager" in app_name or "this pc" in app_name:
            subprocess.Popen(["explorer.exe"])
            return "Opening File Explorer."

        elif "code" in app_name or "vs code" in app_name:
            os.system("code")
            return "Opening Visual Studio Code."

        else:
            os.system(f"start {app_name}")
            return f"Attempting to launch {app_name}."

    except Exception as e:
        return f"Failed to open {app_name}. Error: {e}"

def set_volume(action: str) -> str:
    """
    Controls master volume using system key presses.
    """
    action = action.lower().strip()

    if "up" in action or "increase" in action:
        for _ in range(5):
            pyautogui.press("volumeup")
        return "Volume increased."

    elif "down" in action or "decrease" in action:
        for _ in range(5):
            pyautogui.press("volumedown")
        return "Volume decreased."

    elif "mute" in action or "unmute" in action:
        pyautogui.press("volumemute")
        return "Volume muted or unmuted."

    return "Invalid volume action."

def lock_system() -> str:
    """
    Locks the Windows workstation instantly.
    """
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Locking system."
    except Exception as e:
        return f"Failed to lock system: {e}"