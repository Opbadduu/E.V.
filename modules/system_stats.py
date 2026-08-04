import psutil

def get_battery_status() -> str:
    battery = psutil.sensors_battery()
    if battery is None:
        return "No battery detected (desktop PC or driver issue)."
    
    percent = battery.percent
    plugged = "plugged in" if battery.power_plugged else "not plugged in"
    return f"Your laptop battery is at {percent}% and is currently {plugged}."

def get_system_stats() -> str:
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    return f"CPU usage is at {cpu_usage}%, and RAM usage is at {ram.percent}%."