import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Import agents
try:
    from backend.agents.orchestrator import OrchestratorAgent
    from backend.agents.ingestion import IngestionAgent
    from backend.agents.retrieval import RetrievalAgent
    from backend.agents.qa import QAAgent
    from backend.agents.summarizer import SummarizerAgent
    from backend.agents.translator import TranslatorAgent
    from backend.agents.data_extraction import DataExtractionAgent
    from backend.agents.email_drafting import EmailDraftingAgent
    from backend.utils.memory import MemoryManager
except ImportError:
    from agents.orchestrator import OrchestratorAgent
    from agents.ingestion import IngestionAgent
    from agents.retrieval import RetrievalAgent
    from agents.qa import QAAgent
    from agents.summarizer import SummarizerAgent
    from agents.translator import TranslatorAgent
    from agents.data_extraction import DataExtractionAgent
    from agents.email_drafting import EmailDraftingAgent
    from utils.memory import MemoryManager

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(title="DocuAgent System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents and managers
orchestrator = OrchestratorAgent()
ingestion = IngestionAgent()
retrieval = RetrievalAgent()
qa_agent = QAAgent()
summarizer = SummarizerAgent()
translator = TranslatorAgent()
data_extractor = DataExtractionAgent()
email_drafter = EmailDraftingAgent()
memory_manager = MemoryManager()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    namespace: Optional[str] = None

class ChatResponse(BaseModel):
    agent: str
    answer: str
    reasoning: str
    logs: List[dict]

@app.get("/health")
async def health():
    status = {
        "backend": "ok",
        "groq_key_set": bool(os.getenv("GROQ_API_KEY")),
        "pinecone_key_set": bool(os.getenv("PINECONE_API_KEY")),
        "pinecone_index": os.getenv("PINECONE_INDEX_NAME", "default"),
    }
    return status

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    temp_path = os.path.join(tempfile.gettempdir(), file.filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        result = ingestion.process_file(temp_path, file.filename)
        return result
    except Exception as e:
        err_str = str(e)
        if "credit" in err_str.lower() or "billing" in err_str.lower() or "quota" in err_str.lower():
            raise HTTPException(status_code=402, detail="Anthropic API has no credits. Please top up your account at console.anthropic.com.")
        raise HTTPException(status_code=500, detail=f"Upload failed: {err_str}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1. Route with Orchestrator
        route_data = orchestrator.route(request.message)
        agent_name = route_data['agent']
        reasoning = route_data['reasoning']
        params = route_data.get('parameters', {})

        logs = [{"agent": "Orchestrator", "action": f"Routed to {agent_name}", "reasoning": reasoning}]
        
        # 2. Delegate to specialized agent
        answer = ""
        
        if agent_name == "retrieval":
            search_results = retrieval.search(request.message, namespace=request.namespace)
            answer = str(search_results)
            logs.append({"agent": "Retrieval", "action": "Performed semantic search", "count": len(search_results)})
            
        elif agent_name == "qa":
            context = retrieval.search(request.message, namespace=request.namespace)
            answer = qa_agent.answer(request.message, context)
            logs.append({"agent": "QA", "action": "Generated grounded answer using context"})
            
        elif agent_name == "summarizer":
            context = retrieval.search("everything", namespace=request.namespace, top_k=20)
            answer = summarizer.summarize(context)
            logs.append({"agent": "Summarizer", "action": "Generated document summary"})
            
        elif agent_name == "translator":
            target_lang = params.get('target_language', 'Spanish')
            answer = translator.translate(request.message, target_lang)
            logs.append({"agent": "Translator", "action": f"Translated to {target_lang}"})
            
        elif agent_name == "data_extraction":
            context = retrieval.search("data, tables, entities", namespace=request.namespace)
            answer = data_extractor.extract(context)
            logs.append({"agent": "DataExtraction", "action": "Extracted structured JSON data"})
            
        elif agent_name == "email_drafting":
            context = retrieval.search(request.message, namespace=request.namespace)
            answer = email_drafter.draft(context, request.message)
            logs.append({"agent": "EmailDrafting", "action": "Drafted professional email"})
            
        else:
            answer = "I'm not sure how to handle that specific request yet."

        # Update memory
        memory_manager.add_user_message(request.session_id, request.message)
        memory_manager.add_ai_message(request.session_id, str(answer))

        return ChatResponse(
            agent=agent_name,
            answer=str(answer),
            reasoning=reasoning,
            logs=logs
        )

    except HTTPException:
        raise
    except Exception as e:
        err_str = str(e)
        if "credit" in err_str.lower() or "billing" in err_str.lower() or "quota" in err_str.lower() or "rate_limit" in err_str.lower():
            raise HTTPException(
                status_code=429,
                detail="⚠️ Groq rate limit or quota exceeded. Please check your plan at https://console.groq.com"
            )
        if "authentication" in err_str.lower() or "api_key" in err_str.lower() or "invalid" in err_str.lower() or "unauthorized" in err_str.lower():
            raise HTTPException(
                status_code=401,
                detail="⚠️ Invalid Groq API key. Please check your GROQ_API_KEY in backend/.env"
            )
        raise HTTPException(status_code=500, detail=f"Server error: {err_str}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
