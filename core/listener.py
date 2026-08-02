import speech_recognition as sr
import os
import sys

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.speaker import speak

def listen():
    """
    Captures audio from the default microphone and converts it to text.
    """
    recognizer = sr.Recognizer()
    
    # Sensitivity tuning: lowers threshold so soft speech isn't skipped
    recognizer.energy_threshold = 300 
    recognizer.dynamic_energy_threshold = False 

    with sr.Microphone() as source:
        print("\n🎙️ Listening... (Speak clearly now)")
        
        try:
            # Short phrase limit so it doesn't hang indefinitely
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=10)
            print("⚡ Recognizing...")
            
            command = recognizer.recognize_google(audio)
            print(f"🗣️ You said: {command}")
            return command.lower()
            
        except sr.WaitTimeoutError:
            print("⏱️ Listening timed out (no speech detected).")
            return ""
        except sr.UnknownValueError:
            print("❓ Couldn't understand audio.")
            return ""
        except sr.RequestError:
            speak("Network error with speech recognition service.")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

# Standalone Test
if __name__ == "__main__":
    speak("Testing microphone system. Speak something into your mic.")
    query = listen()
    if query:
        speak(f"I heard you say: {query}")
    else:
        speak("I didn't catch anything.")