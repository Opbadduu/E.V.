import os
import sys
from groq import Groq

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ASSISTANT_NAME
from utils.network import is_online

# Fetch key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_ai(prompt: str) -> str:
    """
    Sends queries to Groq API using the ultra-fast Llama-3.3-70b model.
    """
    if not is_online():
        return "I'm currently offline, boss. Connect to the internet for cloud queries."

    if not GROQ_API_KEY:
        return "Groq API key is missing in your .env file."

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        system_instruction = (
            f"You are {ASSISTANT_NAME}, an intelligent desktop voice assistant inspired by JARVIS. "
            "Keep your answers brief, clear, and direct (1 to 2 sentences maximum) so they are suitable for speaking out loud."
        )
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Groq API Error: {e}")
        return "I hit a glitch reaching my cloud brain."

# Standalone Test
if __name__ == "__main__":
    test_query = "What is the speed of light?"
    print(f"Query: {test_query}")
    print(f"Response: {ask_ai(test_query)}")