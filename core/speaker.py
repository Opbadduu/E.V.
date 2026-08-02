import pyttsx3
import os
import sys

# Add root folder to python path so we can import config cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import VOICE_SPEED, ASSISTANT_NAME

# Initialize pyttsx3 engine
engine = pyttsx3.init()

# Set speaking speed
engine.setProperty("rate", VOICE_SPEED)

# Set voice (Optional: change index 0 to 1 for female voice if available on system)
voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)

def speak(text: str):
    """
    Prints E.V.'s response to the console and speaks it out loud.
    """
    if not text:
        return
    print(f"🤖 {ASSISTANT_NAME}: {text}")
    engine.say(text)
    engine.runAndWait()

# Standalone Test
if __name__ == "__main__":
    speak("Systems online. Hello boss, I am E.V., your virtual assistant.")