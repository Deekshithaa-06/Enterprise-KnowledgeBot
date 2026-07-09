# 🚀 KnowledgeBot - AI Powered Enterprise Knowledge Management System

KnowledgeBot is an AI-powered Enterprise Knowledge Management System that enables users to interact with organizational documents through natural language conversations. Built using a Retrieval-Augmented Generation (RAG) architecture, the application allows users to upload enterprise documents, ask questions, and receive accurate, source-grounded responses with citations.

Unlike traditional chatbots, KnowledgeBot retrieves relevant information from uploaded documents before generating responses, ensuring that answers are based on organizational knowledge rather than the model's general training data.

---

# 📖 Features

- 🔐 User Registration and Login
- 📄 Upload and manage enterprise documents
- 📚 Supports multiple document formats
  - PDF
  - DOCX
  - PPTX
  - XLSX
  - CSV
  - TXT
- 🤖 AI-powered Question Answering
- 🔍 Retrieval-Augmented Generation (RAG)
- 🧠 Semantic Search using Gemini Embeddings
- 🔎 BM25 Keyword Search
- 🔄 Hybrid Retrieval (Semantic + Keyword Search)
- 📌 Source Citations with every response
- 📊 Automatic Chart Generation for numerical queries
- 🗂 Document Management (Upload, View, Delete)
- 🌙 Dark/Light Theme
- 💬 Chat History
- ⏳ Session Continuation Prompt
- ⚙ Runtime Gemini API Key Configuration

---

# 🏗 System Architecture

```
                 User
                   │
                   ▼
        React Frontend (Vite)
                   │
             REST APIs
                   │
                   ▼
            FastAPI Backend
                   │
      ┌────────────┴────────────┐
      │                         │
Document Processing        Query Processing
      │                         │
      ▼                         ▼
 Document Chunking       Hybrid Retrieval
      │                  (BM25 + Embeddings)
      ▼                         │
 Gemini Embeddings              ▼
      │                  Google Gemini LLM
      ▼                         │
 SQLite Database                ▼
                   AI Generated Response
                           +
                      Source Citations
```

---

# 🛠 Technology Stack

## Frontend

- React.js
- Vite
- JavaScript
- CSS
- Lucide React
- Recharts

## Backend

- FastAPI
- Python
- Uvicorn

## AI Services

- Google Gemini
- Gemini Embedding Model

## Database

- SQLite

## Retrieval

- RAG
- BM25
- Cosine Similarity Search

## Document Processing

- PyMuPDF
- python-docx
- python-pptx
- pandas
- openpyxl

---

# 📁 Project Structure

```
KnowledgeBot/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── document_processor.py
│   ├── gemini_service.py
│   ├── vector_store.py
│   ├── requirements.txt
│   ├── uploads/
│   └── knowledge_bot.db
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── dist/
│
├── README.md
└── Documentation/
```

---

# ⚙ Prerequisites

Before running the project, install the following software:

- Python 3.11 or above
- Node.js 18 or above
- npm
- Git
- Google Gemini API Key

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Deekshithaa-06/Enterprise-KnowledgeBot.gitEnterprise_Knowledge_Bot

cd Enterprise_Knowledge_Bot
```

---

## 2. Backend Setup

Navigate to the backend directory.

```bash
cd backend
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Create a `.env` file inside the backend folder.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

---

## 4. Start Backend

```bash
uvicorn backend.main:app --reload
```

Backend runs on

```
http://localhost:8000
```

---

## 5. Frontend Setup

Open another terminal.

```bash
cd frontend
```

Install dependencies.

```bash
npm install
```

Start the frontend.

```bash
npm run dev
```

Frontend runs on

```
http://localhost:5173
```

---

# ▶ Using KnowledgeBot

1. Register a new account or log in.
2. Upload one or more supported documents.
3. Wait until the document status changes to **Active**.
4. Ask questions in natural language.
5. View AI-generated responses with source citations.
6. Delete documents or manage uploaded files when required.

---

# 📂 Supported Document Types

| Format | Supported |
|---------|-----------|
| PDF | ✅ |
| DOCX | ✅ |
| PPTX | ✅ |
| XLSX | ✅ |
| CSV | ✅ |
| TXT | ✅ |

---

# 🧠 How It Works

1. User uploads a document.
2. Text is extracted from the document.
3. The document is divided into smaller chunks.
4. Embeddings are generated using Google's Gemini Embedding Model.
5. Chunks and embeddings are stored in the SQLite database.
6. User submits a question.
7. Hybrid Retrieval (BM25 + Semantic Search) identifies relevant document chunks.
8. Google Gemini generates a grounded response.
9. The chatbot returns the answer along with source citations.

---

# 🔗 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/upload` | Upload a document |
| POST | `/api/query` | Submit a question |
| GET | `/api/documents` | Retrieve uploaded documents |
| DELETE | `/api/documents/{id}` | Delete a document |
| GET | `/api/settings` | Retrieve application settings |
| POST | `/api/settings` | Update application settings |

---

# 📊 Current Features

- User Authentication
- Enterprise Document Management
- Retrieval-Augmented Generation (RAG)
- Google Gemini Integration
- Hybrid Search
- Source Citations
- Document Indexing
- Chat History
- Session Continuation
- Theme Switching
- Runtime API Key Configuration

---

# 🚧 Future Enhancements

- Improved duplicate detection using complete file-content SHA-256 hashing
- Dynamic chat history retention
- Faster backend response time
- Answer confidence score
- Fact validation
- Incorrect information detection
- Corrected answer suggestions
- Suspicious content review panel
- OCR support for scanned documents
- Multilingual support

---

---

# 👨‍💻 Developed By

**KnowledgeBot Development Team**

AI Powered Enterprise Knowledge Management System

---

# 📄 License

This project was developed for academic and learning purposes as part of an internship/project submission.

---

# ⭐ Acknowledgements

- Google Gemini API
- FastAPI
- React.js
- Vite
- SQLite
- Python Community
- Open Source Libraries

---

If you found this project helpful, consider ⭐ starring the repository.