import unittest
import os
import tempfile
import json
from pathlib import Path

# Set up test environment before importing database/config
os.environ["GEMINI_API_KEY"] = "" # Empty for testing
from backend.config import settings

# Override DB path for unit tests to avoid polluting dev DB
temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
temp_db.close()
settings.DB_PATH = Path(temp_db.name)

from backend.database import (
    init_db,
    add_document,
    update_document_status,
    get_all_documents,
    get_document_by_hash,
    add_document_chunks,
    get_all_chunks_with_embeddings
)
from backend.document_processor import calculate_file_hash, chunk_text, process_document
from backend.vector_store import keyword_search_fallback

class TestKnowledgeBotBackend(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize test database
        init_db()

    @classmethod
    def tearDownClass(cls):
        # Remove test database
        if os.path.exists(settings.DB_PATH):
            try:
                os.unlink(settings.DB_PATH)
            except Exception:
                pass

    def test_file_hashing(self):
        content_1 = b"Hello, KnowledgeBot!"
        content_2 = b"Hello, KnowledgeBot!"
        content_3 = b"Different content."
        
        hash_1 = calculate_file_hash(content_1)
        hash_2 = calculate_file_hash(content_2)
        hash_3 = calculate_file_hash(content_3)
        
        self.assertEqual(hash_1, hash_2)
        self.assertNotEqual(hash_1, hash_3)
        self.assertEqual(len(hash_1), 64) # SHA-256 length in hex

    def test_text_chunking(self):
        long_text = "Word " * 200 # 200 words, roughly 1000 characters
        chunks = chunk_text(long_text, max_chars=300, overlap=50)
        
        self.assertTrue(len(chunks) > 1)
        for chunk in chunks:
            self.assertTrue(len(chunk) <= 300)
            
    def test_database_flow(self):
        # Add a new document
        doc_name = "test_doc.txt"
        file_hash = "fakehash123456789"
        file_type = "txt"
        
        doc_id = add_document(doc_name, file_hash, file_type)
        self.assertIsNotNone(doc_id)
        
        # Verify duplicate check
        existing = get_document_by_hash(file_hash)
        self.assertIsNotNone(existing)
        self.assertEqual(existing["filename"], doc_name)
        
        # Update status
        update_document_status(doc_id, "active")
        
        # Add chunks
        chunks = [
            {
                "doc_id": doc_id,
                "chunk_index": 0,
                "text": "This is chunk number one of the document content.",
                "page_number": "Page 1",
                "section_heading": "Introduction",
                "embedding": [0.1, 0.2, 0.3]
            },
            {
                "doc_id": doc_id,
                "chunk_index": 1,
                "text": "This is chunk number two detailing some sales statistics. Sales grew by 15 percent.",
                "page_number": "Page 2",
                "section_heading": "Sales Reports",
                "embedding": [0.4, 0.5, 0.6]
            }
        ]
        add_document_chunks(chunks)
        
        # Retrieve and verify
        all_docs = get_all_documents()
        self.assertTrue(len(all_docs) >= 1)
        
        all_chunks = get_all_chunks_with_embeddings()
        self.assertEqual(len(all_chunks), 2)
        self.assertEqual(all_chunks[0]["filename"], doc_name)
        self.assertEqual(all_chunks[1]["section_heading"], "Sales Reports")
        self.assertEqual(all_chunks[0]["embedding"], [0.1, 0.2, 0.3])

    def test_keyword_search_fallback(self):
        chunks = [
            {"text": "Apple computer sales skyrocketed in the fourth quarter.", "filename": "apple.txt"},
            {"text": "Bananas are rich in potassium and are a popular tropical fruit.", "filename": "banana.txt"},
            {"text": "Oranges contain high amounts of Vitamin C.", "filename": "orange.txt"}
        ]
        
        # Query matching "Apple"
        results_apple = keyword_search_fallback("apple computer", chunks, top_k=2)
        self.assertEqual(len(results_apple), 1)
        self.assertEqual(results_apple[0]["filename"], "apple.txt")
        
        # Query matching "fruit"
        results_fruit = keyword_search_fallback("potassium fruit", chunks, top_k=2)
        self.assertEqual(len(results_fruit), 1)
        self.assertEqual(results_fruit[0]["filename"], "banana.txt")

if __name__ == "__main__":
    unittest.main()
