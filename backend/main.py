import shutil
import mimetypes
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database import (
    init_db,
    add_document,
    update_document_status,
    get_all_documents,
    delete_document,
    get_document_by_hash,
    add_document_chunks
)
from backend.document_processor import calculate_file_hash, process_document
from backend.vector_store import get_embeddings_batch, search_similar_chunks
from backend.gemini_service import generate_answer_from_context

app = FastAPI(title=settings.PROJECT_NAME)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev, allow all origins. Can be restricted to Vite port if needed.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class SettingsRequest(BaseModel):
    api_key: str

@app.on_event("startup")
def startup_event():
    # Initialize the database and create tables if not present
    init_db()

@app.get("/api/settings")
def get_settings():
    """Check if Gemini API key is configured."""
    has_key = len(settings.GEMINI_API_KEY) > 0
    return {"has_api_key": has_key}

@app.post("/api/settings")
def save_settings(req: SettingsRequest):
    """Save Gemini API key to .env file."""
    if not req.api_key.strip():
        raise HTTPException(status_code=400, detail="API Key cannot be empty.")
    settings.set_api_key(req.api_key.strip())
    return {"status": "success", "message": "API Key saved successfully."}

@app.get("/api/documents")
def list_documents():
    """Retrieve all uploaded documents."""
    return get_all_documents()

@app.delete("/api/documents/{doc_id}")
def remove_document(doc_id: int):
    """Delete a document and clean up its stored file."""
    # Find the document info to delete file from disk
    docs = get_all_documents()
    target_doc = next((d for d in docs if d["id"] == doc_id), None)
    
    # Delete from database (cascades to chunks)
    delete_document(doc_id)
    
    # Delete file from upload directory
    if target_doc:
        file_path = settings.UPLOAD_DIR / target_doc["filename"]
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
                
    return {"status": "success", "message": "Document deleted successfully."}

@app.get("/api/documents/{doc_id}/open")
def open_document(doc_id: int):
    """Return the uploaded file so the frontend can open it in the browser."""
    docs = get_all_documents()
    target_doc = next((d for d in docs if d["id"] == doc_id), None)

    if not target_doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    file_path = settings.UPLOAD_DIR / target_doc["filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Uploaded file not found on disk.")

    media_type, _ = mimetypes.guess_type(file_path.name)

    return FileResponse(
        path=file_path,
        filename=target_doc["filename"],
        media_type=media_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{target_doc["filename"]}"'}
    )

def process_uploaded_document_task(doc_id: int, file_path: Path, file_type: str):
    """Background task to extract text, generate embeddings, and store in database."""
    try:
        # Extract text and chunk it
        chunks_data = process_document(file_path, file_type)
        if not chunks_data:
            update_document_status(doc_id, "error")
            return
            
        # Extract raw texts for batch embedding
        texts = [c["text"] for c in chunks_data]
        
        # Generate embeddings
        embeddings = get_embeddings_batch(texts)
        
        # Prepare list of database chunk records
        db_chunks = []
        for idx, chunk in enumerate(chunks_data):
            emb = embeddings[idx] # Might be None if API key missing
            db_chunks.append({
                "doc_id": doc_id,
                "chunk_index": idx,
                "text": chunk["text"],
                "page_number": chunk.get("page_number"),
                "section_heading": chunk.get("section_heading"),
                "embedding": emb
            })
            
        # Store chunks in database
        add_document_chunks(db_chunks)
        update_document_status(doc_id, "active")
        
    except Exception as e:
        print(f"Error processing document task (ID {doc_id}): {e}")
        update_document_status(doc_id, "error")

@app.post("/api/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload a document with duplicate detection and asynchronous chunking/embedding."""
    filename = file.filename
    # Verify extension
    suffix = Path(filename).suffix.lower()
    allowed_suffixes = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', '.csv', '.txt', '.md']
    if suffix not in allowed_suffixes:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{suffix}'. Supported formats are: PDF, DOCX, PPTX, XLSX, CSV, TXT"
        )
        
    # Read file content to check hash
    file_bytes = await file.read()
    file_hash = calculate_file_hash(file_bytes)
    
    # Check for duplicate by hash OR filename
    existing_docs = get_all_documents()
    existing_doc = next((d for d in existing_docs if d["file_hash"] == file_hash or d["filename"] == filename), None)
    
    if existing_doc:
        if existing_doc["status"] == "active":
            raise HTTPException(
                status_code=409,
                detail=f"Duplicate document detected. '{filename}' has already been indexed."
            )
        elif existing_doc["status"] == "processing":
            raise HTTPException(
                status_code=409,
                detail=f"'{filename}' is currently being processed. Please wait."
            )
        else:
            # If it was in error state, delete the old entry and re-upload
            delete_document(existing_doc["id"])
            
    # Save the file to upload directory
    dest_path = settings.UPLOAD_DIR / filename
    with open(dest_path, "wb") as buffer:
        buffer.write(file_bytes)
        
    # Insert document record with 'processing' status
    doc_id = add_document(filename, file_hash, suffix)
    
    # Add extraction & indexing as a background task to keep upload endpoint fast
    background_tasks.add_task(process_uploaded_document_task, doc_id, dest_path, suffix)
    
    return {
        "status": "success",
        "doc_id": doc_id,
        "filename": filename,
        "message": "Document uploaded successfully. Processing started in the background."
    }

@app.post("/api/query")
def query_knowledge_base(req: QueryRequest):
    """Query the knowledge base, retrieve relevant chunks, and generate a response."""
    query = req.query
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    # Retrieve top K similar chunks
    retrieved_chunks = search_similar_chunks(query, top_k=req.top_k)
    
    # Synthesize answer using Gemini
    result = generate_answer_from_context(query, retrieved_chunks)
    
    # Format and return response
    return {
        "query": query,
        "answer": result.get("answer"),
        "citations": result.get("citations", []),
        "chart": result.get("chart"),
        "retrieved_chunks": [
            {
                "filename": chunk["filename"],
                "text": chunk["text"],
                "page_number": chunk.get("page_number"),
                "section_heading": chunk.get("section_heading"),
                "score": chunk.get("similarity_score", 0.0)
            } for chunk in retrieved_chunks
        ]
    }
