import os
from dotenv import load_dotenv

# Load .env file at the root level
load_dotenv()

ASSISTANT_NAME = "E.V."
VOICE_SPEED = 175
GROQ_API_KEY = os.getenv("GROQ_API_KEY")