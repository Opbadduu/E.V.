import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Voice Assistant Configurations
ASSISTANT_NAME = "E.V."
VOICE_SPEED = 175  # Speaking rate (150-200 WPM is natural)