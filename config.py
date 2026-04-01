import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
# Vertex AI uses Application Default Credentials (ADC), not an API key.
# Run: gcloud auth application-default login
