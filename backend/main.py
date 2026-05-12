import os
import json
import shutil
import tempfile
from datetime import datetime, timezone

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# ── Agent imports (supports both module and direct execution) ─────────────────
try:
    from backend.agents.orchestrator import OrchestratorAgent
    from backend.agents.ingestion import IngestionAgent
    from backend.agents.retrieval import RetrievalAgent
    from backend.agents.qa import QAAgent
    from backend.agents.summarizer import SummarizerAgent
    from backend.agents.translator import TranslatorAgent
    from backend.agents.data_extraction import DataExtractionAgent
    from backend.agents.email_drafting import EmailDraftingAgent
    from backend.agents.comparison import ComparisonAgent
    from backend.utils.memory import MemoryManager
    from backend.utils.document_registry import (
        register_document, list_documents, delete_document
    )
    from backend.utils.pinecone_client import PineconeClient
except ImportError:
    from agents.orchestrator import OrchestratorAgent
    from agents.ingestion import IngestionAgent
    from agents.retrieval import RetrievalAgent
    from agents.qa import QAAgent
    from agents.summarizer import SummarizerAgent
    from agents.translator import TranslatorAgent
    from agents.data_extraction import DataExtractionAgent
    from agents.email_drafting import EmailDraftingAgent
    from agents.comparison import ComparisonAgent
    from utils.memory import MemoryManager
    from utils.document_registry import (
        register_document, list_documents, delete_document
    )
    from utils.pinecone_client import PineconeClient

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(title="DocuAgent System API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Agent & utility singletons ────────────────────────────────────────────────
orchestrator  = OrchestratorAgent()
ingestion     = IngestionAgent()
retrieval     = RetrievalAgent()
qa_agent      = QAAgent()
summarizer    = SummarizerAgent()
translator    = TranslatorAgent()
data_extractor = DataExtractionAgent()
email_drafter = EmailDraftingAgent()
comparator    = ComparisonAgent()
memory_manager = MemoryManager()
pc_client     = PineconeClient()

# ── Pydantic models ───────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str
    namespace: Optional[str] = None
    compare_namespace: Optional[str] = None  # second doc for comparison

class ChatResponse(BaseModel):
    agent: str
    answer: str
    reasoning: str
    logs: List[dict]

class ExportRequest(BaseModel):
    session_id: str
    format: str = "markdown"   # "markdown" | "json"


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "backend": "ok",
        "groq_key_set": bool(os.getenv("GROQ_API_KEY")),
        "pinecone_key_set": bool(os.getenv("PINECONE_API_KEY")),
        "pinecone_index": os.getenv("PINECONE_INDEX_NAME", "default"),
    }


# ── Upload ────────────────────────────────────────────────────────────────────
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    temp_path = os.path.join(tempfile.gettempdir(), file.filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        result = ingestion.process_file(temp_path, file.filename)
        # Persist to registry
        register_document(
            doc_id=result["doc_id"],
            doc_name=result["doc_name"],
            chunk_count=result.get("chunks", 0),
        )
        return result
    except Exception as e:
        err_str = str(e)
        if "credit" in err_str.lower() or "billing" in err_str.lower() or "quota" in err_str.lower():
            raise HTTPException(status_code=402, detail="API quota exceeded.")
        raise HTTPException(status_code=500, detail=f"Upload failed: {err_str}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ── Document Manager ──────────────────────────────────────────────────────────
@app.get("/documents")
async def get_documents():
    """Return all registered documents with metadata."""
    return {"documents": list_documents()}


@app.delete("/documents/{doc_id}")
async def delete_document_endpoint(doc_id: str):
    """Delete a document's vectors from Pinecone and remove from registry."""
    try:
        pc_client.delete_namespace(doc_id)
    except Exception as e:
        # Namespace may not exist in Pinecone — log and continue
        print(f"[Delete] Pinecone namespace deletion warning: {e}")

    removed = delete_document(doc_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found in registry.")
    return {"status": "deleted", "doc_id": doc_id}


# ── Chat ──────────────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        route_data  = orchestrator.route(request.message)
        agent_name  = route_data["agent"]
        reasoning   = route_data["reasoning"]
        params      = route_data.get("parameters", {})

        logs = [{"agent": "Orchestrator", "action": f"Routed to {agent_name}", "reasoning": reasoning}]

        # Fetch conversation history for memory-aware agents
        history = memory_manager.get_context(request.session_id)

        answer = ""

        if agent_name == "retrieval":
            results = retrieval.search(request.message, namespace=request.namespace)
            answer  = str(results)
            logs.append({"agent": "Retrieval", "action": "Performed semantic search", "count": len(results)})

        elif agent_name == "qa":
            context = retrieval.search(request.message, namespace=request.namespace)
            answer  = qa_agent.answer(request.message, context, history=history)
            logs.append({"agent": "QA", "action": "Generated grounded answer with conversation context"})

        elif agent_name == "summarizer":
            context = retrieval.search("everything", namespace=request.namespace, top_k=20)
            answer  = summarizer.summarize(context, history=history)
            logs.append({"agent": "Summarizer", "action": "Generated document summary"})

        elif agent_name == "translator":
            target_lang = params.get("target_language", "Spanish")
            answer = translator.translate(request.message, target_lang)
            logs.append({"agent": "Translator", "action": f"Translated to {target_lang}"})

        elif agent_name == "data_extraction":
            context = retrieval.search("data, tables, entities", namespace=request.namespace)
            answer  = data_extractor.extract(context)
            logs.append({"agent": "DataExtraction", "action": "Extracted structured JSON data"})

        elif agent_name == "email_drafting":
            context = retrieval.search(request.message, namespace=request.namespace)
            answer  = email_drafter.draft(context, request.message, history=history)
            logs.append({"agent": "EmailDrafting", "action": "Drafted professional email"})

        elif agent_name == "comparison":
            if not request.compare_namespace:
                answer = "⚠️ Please select a second document to compare against."
            else:
                chunks_a = retrieval.search(request.message, namespace=request.namespace, top_k=8)
                chunks_b = retrieval.search(request.message, namespace=request.compare_namespace, top_k=8)
                doc_a_name = chunks_a[0]["doc_name"] if chunks_a else "Document A"
                doc_b_name = chunks_b[0]["doc_name"] if chunks_b else "Document B"
                answer = comparator.compare(
                    chunks_a, chunks_b,
                    query=request.message,
                    doc_a_name=doc_a_name,
                    doc_b_name=doc_b_name,
                    history=history,
                )
            logs.append({"agent": "Comparison", "action": "Compared two documents"})

        else:
            answer = "I'm not sure how to handle that request."

        # Update conversation memory
        memory_manager.add_user_message(request.session_id, request.message)
        memory_manager.add_ai_message(request.session_id, str(answer))

        return ChatResponse(agent=agent_name, answer=str(answer), reasoning=reasoning, logs=logs)

    except HTTPException:
        raise
    except Exception as e:
        err_str = str(e)
        if any(k in err_str.lower() for k in ("rate_limit", "quota", "credit", "billing")):
            raise HTTPException(status_code=429, detail="⚠️ Groq rate limit exceeded. Check console.groq.com")
        if any(k in err_str.lower() for k in ("authentication", "api_key", "invalid", "unauthorized")):
            raise HTTPException(status_code=401, detail="⚠️ Invalid Groq API key. Check backend/.env")
        raise HTTPException(status_code=500, detail=f"Server error: {err_str}")


# ── Streaming Chat ─────────────────────────────────────────────────────────────
@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE streaming endpoint — emits tokens as they arrive from Groq.
    The client reads this as a text/event-stream.
    Each event: `data: <token>\n\n`
    Final event: `data: [DONE]\n\n`
    """
    import groq as groq_sdk

    route_data = orchestrator.route(request.message)
    agent_name = route_data["agent"]
    history    = memory_manager.get_context(request.session_id)

    # Build the prompt content for streaming (QA path as default for stream)
    context_chunks = retrieval.search(request.message, namespace=request.namespace, top_k=5)
    context_text   = "\n\n".join(
        [f"Source: {c['doc_name']}\nContent: {c['text']}" for c in context_chunks]
    )
    history_block = ""
    if history:
        lines = []
        for msg in history[-(10):]:
            role = "User" if msg.type == "human" else "Assistant"
            lines.append(f"{role}: {msg.content}")
        if lines:
            history_block = "Previous conversation:\n" + "\n".join(lines) + "\n\n"

    system_prompt = (
        "You are a helpful document assistant. Answer based ONLY on the provided context. "
        "Cite source document names when possible."
    )
    user_content = (
        f"{history_block}"
        f"Document Context:\n{context_text}\n\n"
        f"Question: {request.message}"
    )

    groq_client = groq_sdk.Groq(api_key=os.getenv("GROQ_API_KEY"))

    async def event_generator():
        full_answer = []
        try:
            stream = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_content},
                ],
                stream=True,
                max_tokens=1024,
            )
            # Send routing metadata first
            meta = json.dumps({"agent": agent_name, "reasoning": route_data.get("reasoning", "")})
            yield f"data: __META__{meta}\n\n"

            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                if token:
                    full_answer.append(token)
                    yield f"data: {token}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: __ERROR__{str(e)}\n\n"
        finally:
            # Persist to memory after streaming completes
            memory_manager.add_user_message(request.session_id, request.message)
            memory_manager.add_ai_message(request.session_id, "".join(full_answer))

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── Chat Export ───────────────────────────────────────────────────────────────
@app.post("/export")
async def export_chat(request: ExportRequest):
    """Export the conversation history as Markdown or JSON."""
    history = memory_manager.get_context(request.session_id)
    if not history:
        raise HTTPException(status_code=404, detail="No conversation history found for this session.")

    if request.format == "json":
        payload = [
            {"role": "user" if m.type == "human" else "assistant", "content": m.content}
            for m in history
        ]
        content = json.dumps(payload, indent=2, ensure_ascii=False)
        media_type = "application/json"
        filename = f"docuagent_chat_{request.session_id[:8]}.json"
    else:
        # Markdown
        lines = [f"# DocuAgent Chat Export\n\n*Exported: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*\n"]
        for msg in history:
            role = "**You**" if msg.type == "human" else "**DocuAgent**"
            lines.append(f"\n---\n\n{role}\n\n{msg.content}\n")
        content = "\n".join(lines)
        media_type = "text/markdown"
        filename = f"docuagent_chat_{request.session_id[:8]}.md"

    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
