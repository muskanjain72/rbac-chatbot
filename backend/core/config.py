import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    # qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    # qdrant_api_key = os.getenv("QDRANT_API_KEY", "")

settings = Settings()