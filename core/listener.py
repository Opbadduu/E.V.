import os
import sys

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def listen() -> str:
    """
    Temporary terminal text listener for testing E.V. commands without a microphone.
    """
    try:
        command = input("\n💬 You (Type command): ").strip()
        return command.lower()
    except (KeyboardInterrupt, EOFError):
        return "exit"

# Standalone Test
if __name__ == "__main__":
    print("Testing terminal text listener...")
    query = listen()
    print(f"Captured command: '{query}'")