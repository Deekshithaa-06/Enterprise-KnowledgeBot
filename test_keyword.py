import sys
sys.path.insert(0, r"c:\Users\s.a.gedela\OneDrive - Accenture\Desktop\Knowledge_Bot_V4")
import sqlite3
from backend.vector_store import keyword_search_fallback

conn = sqlite3.connect('backend/knowledge_bot.db')
c = conn.cursor()
rows = c.execute("SELECT id, text FROM document_chunks").fetchall()
chunks = [{"id": r[0], "text": r[1]} for r in rows]

query = "Who is the author of the knowledge bot brd?"
top = keyword_search_fallback(query, chunks, 15)

for chunk in top:
    if "Deekshitha" in chunk["text"]:
        print("FOUND DEEKSHITHA! Score:", chunk.get("similarity_score"))
    if "[Member 1 Name]" in chunk["text"]:
        print("FOUND MEMBER! Score:", chunk.get("similarity_score"))
