import sqlite3

def clear_all_embeddings():
    conn = sqlite3.connect('backend/knowledge_bot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE document_chunks SET embedding = NULL")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Cleared embeddings for {count} chunks.")

if __name__ == "__main__":
    clear_all_embeddings()
