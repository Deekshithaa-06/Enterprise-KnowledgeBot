import sys
import os
sys.path.insert(0, r"c:\Users\s.a.gedela\OneDrive - Accenture\Desktop\Knowledge_Bot_V4")
from backend.config import settings
from google import genai
client = genai.Client(api_key=settings.GEMINI_API_KEY)
try:
    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=["Hello", "World"]
    )
    print("Success!", response)
except Exception as e:
    print("Failed:", e)
