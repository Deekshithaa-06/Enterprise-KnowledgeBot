import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable WAL mode for concurrency
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    # Create documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            file_type TEXT NOT NULL,
            upload_time TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    
    # Create document_chunks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            page_number TEXT,
            section_heading TEXT,
            embedding TEXT, -- JSON array of floats
            FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """)
    
    # Indexing for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON document_chunks(doc_id)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_docs_hash ON documents(file_hash)")
    
    conn.commit()
    conn.close()

def add_document(filename: str, file_hash: str, file_type: str) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    upload_time = datetime.now().isoformat()
    try:
        cursor.execute(
            "INSERT INTO documents (filename, file_hash, file_type, upload_time, status) VALUES (?, ?, ?, ?, ?)",
            (filename, file_hash, file_type, upload_time, "processing")
        )
        doc_id = cursor.lastrowid
        conn.commit()
        return doc_id
    except sqlite3.IntegrityError:
        # File with same hash already exists
        cursor.execute("SELECT id FROM documents WHERE file_hash = ?", (file_hash,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        raise
    finally:
        conn.close()

def update_document_status(doc_id: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET status = ? WHERE id = ?", (status, doc_id))
    conn.commit()
    conn.close()

def get_document_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE file_hash = ?", (file_hash,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_all_documents() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY upload_time DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_document(doc_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete chunks first (due to cascade, but good to be explicit)
    cursor.execute("DELETE FROM document_chunks WHERE doc_id = ?", (doc_id,))
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()

def add_document_chunks(chunks: List[Dict[str, Any]]):
    """
    chunks is a list of dicts:
    [
        {
            "doc_id": int,
            "chunk_index": int,
            "text": str,
            "page_number": str,
            "section_heading": str,
            "embedding": List[float]
        }
    ]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Prepare tuples for executemany
    records = []
    for c in chunks:
        emb_str = json.dumps(c["embedding"]) if c.get("embedding") else None
        records.append((
            c["doc_id"],
            c["chunk_index"],
            c["text"],
            c.get("page_number"),
            c.get("section_heading"),
            emb_str
        ))
        
    cursor.executemany(
        """
        INSERT INTO document_chunks (doc_id, chunk_index, text, page_number, section_heading, embedding)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        records
    )
    conn.commit()
    conn.close()

def get_all_chunks_with_embeddings() -> List[Dict[str, Any]]:
    """Returns all active chunks. Embedding field will be [] if not yet generated."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.doc_id, c.chunk_index, c.text, c.page_number, c.section_heading, c.embedding, d.filename
        FROM document_chunks c
        JOIN documents d ON c.doc_id = d.id
        WHERE d.status = 'active'
    """)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        item = dict(r)
        # Parse JSON string back to list of floats (None if embedding not generated)
        item["embedding"] = json.loads(item["embedding"]) if item["embedding"] else []
        result.append(item)
    return result
