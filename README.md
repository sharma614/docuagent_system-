# 🤖 DocuAgent — Multi-Agent AI Document System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://react.dev)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3-orange)](https://groq.com)
[![Pinecone](https://img.shields.io/badge/Vector%20DB-Pinecone-green)](https://pinecone.io)

A production-ready, multi-agent AI system for intelligent document processing. Upload PDFs, DOCX, or TXT files and interact with them through 8 specialized AI agents — all powered by **Groq (Llama 3.3 70B)** and **Pinecone** vector search.

---

## ✨ Features

- 📄 **Multi-document management** with per-document Pinecone namespaces
- 🧠 **8 specialized AI agents** orchestrated intelligently
- 💬 **Real-time chat interface** with source citations
- 📊 **Agent Activity Log** — see exactly which agent handled your request and why
- 🔍 **Semantic search** using `all-MiniLM-L6-v2` embeddings (384-dim)
- 🌗 **Dark theme UI** with glassmorphism and animations

---

## 🤖 Agent Overview

| Agent | Trigger | What it does |
|---|---|---|
| **Orchestrator** | Every message | Routes to the correct agent using LLM reasoning |
| **Ingestion** | File upload | Parses PDF/DOCX/TXT, chunks, embeds & stores in Pinecone |
| **Retrieval** | Search queries | Semantic vector search across documents |
| **QA** | Specific questions | Grounded answers from document context |
| **Summarizer** | "Summarize..." | Concise summary + key bullet points |
| **Translator** | "Translate to..." | Detects source language, translates content |
| **Data Extraction** | "Extract data..." | Returns structured JSON of tables, KV pairs, entities |
| **Email Drafting** | "Draft an email..." | Professional email based on document context |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│                  Frontend                    │
│         React + Vite + Tailwind CSS          │
│   Sidebar │ Chat Interface │ Agent Activity  │
└─────────────────┬──────────────────────────┘
                  │ HTTP (localhost:8000)
┌─────────────────▼──────────────────────────┐
│              FastAPI Backend                 │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │          Orchestrator Agent           │   │
│  │    (Groq Llama 3.3 70B — routing)    │   │
│  └──┬──────────────────────────────┬───┘   │
│     │                              │         │
│  ┌──▼───────┐  ┌──────────┐  ┌───▼──────┐  │
│  │   QA     │  │Summarizer│  │Translator│  │
│  │ Email    │  │Retrieval │  │DataExtract│  │
│  └──────────┘  └────┬─────┘  └──────────┘  │
│                     │                        │
│  ┌──────────────────▼─────────────────────┐  │
│  │         Sentence Transformers           │  │
│  │        (all-MiniLM-L6-v2, 384-dim)     │  │
│  └──────────────────┬────────────────────┘  │
└─────────────────────┼─────────────────────┘
                      │
          ┌───────────▼──────────┐
          │   Pinecone (Vector DB) │
          │  Per-document namespaces│
          └──────────────────────┘
```

---

## 🚀 Local Setup & Workflow

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Groq API key](https://console.groq.com) (free)
- [Pinecone API key](https://app.pinecone.io) (free tier)

### Step 1 — Clone the repo
```bash
git clone https://github.com/sharma614/docuagent_system-.git
cd docuagent_system-
```

### Step 2 — Backend setup
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 3 — Configure environment variables
```bash
# Copy the example file
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=default
PORT=8000
```

> **Note:** The Pinecone index is created automatically on first run if it doesn't exist (384 dimensions, cosine metric, AWS us-east-1).

### Step 4 — Start the backend
```bash
# From the project root
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`  
Interactive API docs: `http://localhost:8000/docs`

### Step 5 — Frontend setup & start
```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## 📋 Complete Usage Workflow

### 1. Upload a Document
Click **"Upload Document"** in the sidebar. Supports: `.pdf`, `.docx`, `.txt`

The system will:
- Extract and chunk the text
- Generate embeddings (`all-MiniLM-L6-v2`)
- Store vectors in Pinecone under a unique namespace for that document

### 2. Chat with Your Documents

Type a message in the chat box and press **Enter**. The Orchestrator automatically routes to the right agent:

| What you type | Agent triggered |
|---|---|
| `"What is the contract value?"` | **QA Agent** |
| `"Summarize this document"` | **Summarizer Agent** |
| `"Translate the findings to French"` | **Translator Agent** |
| `"Extract all tables and data"` | **Data Extraction Agent** |
| `"Draft a follow-up email"` | **Email Drafting Agent** |
| `"Find anything about penalties"` | **Retrieval Agent** |

### 3. Monitor Agent Activity
The **Agent Activity** panel (right side) shows real-time logs of:
- Which agent was selected by the Orchestrator
- The reasoning behind the routing decision
- Actions taken by each agent

---

## 📁 Project Structure

```
docuagent-system/
├── backend/
│   ├── agents/
│   │   ├── orchestrator.py      # Routes requests to correct agent
│   │   ├── ingestion.py         # Parses & embeds uploaded documents
│   │   ├── retrieval.py         # Semantic vector search
│   │   ├── qa.py                # Grounded Q&A from context
│   │   ├── summarizer.py        # Document summarization
│   │   ├── translator.py        # Multi-language translation
│   │   ├── data_extraction.py   # Structured data extraction (JSON)
│   │   └── email_drafting.py    # Professional email generation
│   ├── utils/
│   │   ├── pinecone_client.py   # Pinecone singleton (auto-creates index)
│   │   ├── embeddings.py        # Sentence-transformer embeddings
│   │   └── memory.py            # Conversation memory manager
│   ├── main.py                  # FastAPI app, routes & error handling
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                     # ← NOT committed (gitignored)
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main app component
│   │   └── ...
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── Dockerfile
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check backend and API key status |
| `GET` | `/docs` | Interactive Swagger UI |
| `POST` | `/upload` | Upload a document file |
| `POST` | `/chat` | Send a message to the agent system |

### Chat Request Example
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize this document",
    "session_id": "my-session-123",
    "namespace": null
  }'
```

### Chat Response
```json
{
  "agent": "summarizer",
  "answer": "The document covers...",
  "reasoning": "User asked to summarize the document...",
  "logs": [
    {"agent": "Orchestrator", "action": "Routed to summarizer", "reasoning": "..."},
    {"agent": "Summarizer", "action": "Generated document summary"}
  ]
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq — Llama 3.3 70B Versatile |
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Vector DB** | Pinecone (Serverless) |
| **Backend** | Python, FastAPI, LangChain |
| **Frontend** | React 18, Vite, Tailwind CSS, Framer Motion |
| **Document Parsing** | PyPDF2, docx2txt |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
