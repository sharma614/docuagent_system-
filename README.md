# DocuAgent System

A production-ready multi-agent AI document system built with FastAPI, React, LangChain, Claude, and Pinecone.

## 🏗️ Architecture

```text
User Request
     │
     ▼
+──────────────+
│ Orchestrator │ ◄── Claude-3-Sonnet
+──────────────+
     │
     ├────────────────┬─────────────────┬───────────────┐
     ▼                ▼                 ▼               ▼
+──────────+    +────────────+    +───────────+    +───────────+
│ Retrieval│    │ QA Agent   │    │ Summarizer│    │ Translator│ ...
+──────────+    +────────────+    +───────────+    +───────────+
     │                │                 │               │
     ▼                ▼                 ▼               ▼
+──────────+    +────────────+    +───────────+    +───────────+
│ Pinecone │    │ Contextual │    │ Multi-Doc │    │  Language │
│ DB       │    │ Reasoning  │    │ Summary   │    │  Detection│
+──────────+    +────────────+    +───────────+    +───────────+
```

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Anthropic API Key
- Pinecone API Key & Index

### Setup
1. Clone the repository.
2. Create `backend/.env` from `backend/.env.example` and fill in your keys.
3. Run with Docker:
   ```bash
   docker-compose up --build
   ```
4. Access the UI at `http://localhost:8000` (or `http://localhost:3000` during dev).

## 🤖 Agents
1. **Orchestrator**: Master router delegating tasks.
2. **Ingestion**: File processing and Pinecone upserting.
3. **Retrieval**: Semantic similarity search.
4. **QA**: Context-grounded answering.
5. **Summarizer**: Document summarization.
6. **Translator**: Multi-language support.
7. **Data Extraction**: Structured JSON extraction.
8. **Email Drafting**: Professional email generation.

## 🎨 UI Features
- Dark theme with glassmorphism.
- Real-time agent activity logs.
- Document management sidebar.
- Responsive design.
