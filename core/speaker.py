import os
import sys
import re
import pyttsx3

# Add root folder to python path so we can import config cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import VOICE_SPEED, ASSISTANT_NAME

def _clean_text_for_speech(text: str) -> str:
    """
    Strips Markdown formatting and cleans up whitespace/newlines
    so pyttsx3 speaks smoothly without cutting off.
    """
    # Remove Markdown bold/italic (* or _) and headers (#)
    cleaned = re.sub(r'[*_#`]', '', text)
    # Replace multiple whitespaces/newlines with a single space
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def speak(text: str):
    """
    Prints E.V.'s formatted response to the console and speaks the cleaned text out loud.
    """
    if not text:
        return

    # Print original formatted response to terminal
    print(f"\n🤖 {ASSISTANT_NAME}: {text}\n")

    # Clean text for speech engine
    speech_text = _clean_text_for_speech(text)

    try:
        # Re-initialize engine instance to prevent audio thread lockups
        engine = pyttsx3.init()
        engine.setProperty("rate", VOICE_SPEED)

        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)

        engine.say(speech_text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"❌ Speech Error: {e}")

# Standalone Test
if __name__ == "__main__":
    test_response = (
        "Systems online. Hello boss, I am E.V., your virtual assistant. "
        "I can read multiple sentences without cutting off now! "
        "Here is an example with **bold text** and multiple lines."
    )
    speak(test_response)