import sys
sys.path.insert(0, r"c:\Users\s.a.gedela\OneDrive - Accenture\Desktop\Knowledge_Bot_V4")
import sqlite3
from backend.config import settings
from google import genai
import time

client = genai.Client(api_key=settings.GEMINI_API_KEY)
conn = sqlite3.connect('backend/knowledge_bot.db')
cursor = conn.cursor()
rows = cursor.execute("SELECT id, text FROM document_chunks").fetchall()

print(f"Re-embedding {len(rows)} chunks with text-embedding-004...")
count = 0
for row_id, text in rows:
    try:
        response = client.models.embed_content(model="models/text-embedding-004", contents=text)
        emb = response.embeddings[0].values
        cursor.execute("UPDATE document_chunks SET embedding = ? WHERE id = ?", (str(emb), row_id))
        count += 1
        time.sleep(1) # avoid rate limit
    except Exception as e:
        print(f"Failed at {row_id}: {e}")

conn.commit()
conn.close()
print(f"Successfully embedded {count}/{len(rows)} chunks.")
