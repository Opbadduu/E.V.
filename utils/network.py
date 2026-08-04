import socket

def is_online():
    """
    Checks if the device is currently connected to the internet.
    """
    try:
        # Attempts to connect to Google's public DNS server on port 53
        socket.create_connection(("8.8.8.8", 53), timeout=2.0)
        return True
    except OSError:
        return False

# Standalone Test
if __name__ == "__main__":
    if is_online():
        print("🌐 Internet connection is active!")
    else:
        print("🔌 Offline mode.")