import os

from dotenv import load_dotenv


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_STT_MODEL = "whisper-large-v3"

LOCAL_STT_MODEL = "small"