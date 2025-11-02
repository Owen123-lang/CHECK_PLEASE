from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agent_core import run_agentic_rag_crew  # Use intelligent CrewAI agent
from starlette.responses import StreamingResponse, Response
from crewai import LLM
import io
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Check Please API",
    description="API for Intelligent Agentic RAG with CrewAI",
    version="0.3.0"  # Version bump for intelligent agent
)

# --- Konfigurasi CORS (DIPERBAIKI) ---
# Tambahkan localhost:3001 karena frontend berjalan di sana
origins = [
    "http://localhost:3000",
    "http://localhost:3001",  # Tambahkan port 3001
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize simple LLM for chitchat (without RAG)
simple_llm = LLM(
    model="gemini/gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)

# --- Model Data Pydantic ---
class QueryRequest(BaseModel):
    message: str
    user_urls: list[str] | None = None

# --- Helper Functions ---
def is_chitchat(query: str) -> bool:
    """
    Determine if a query is simple chitchat or requires RAG.
    Returns True for chitchat, False for specific questions.
    """
    query_lower = query.lower().strip()
    
    # Common chitchat patterns
    chitchat_keywords = [
        'halo', 'hai', 'hello', 'hi', 'hey',
        'selamat pagi', 'selamat siang', 'selamat malam',
        'good morning', 'good afternoon', 'good evening',
        'apa kabar', 'how are you',
        'test', 'testing', 'tes',
        'terima kasih', 'thank you', 'thanks',
        'bye', 'goodbye', 'sampai jumpa'
    ]
    
    # Check if query is very short (likely chitchat)
    if len(query_lower.split()) <= 3:
        for keyword in chitchat_keywords:
            if keyword in query_lower:
                return True
    
    # If user provides URLs, definitely not chitchat
    return False

def handle_chitchat(query: str) -> str:
    """
    Handle simple chitchat using LLM directly (no RAG).
    """
    try:
        prompt = f"""You are a friendly AI assistant named "Check Please". 
Respond naturally and briefly to this greeting or casual message: "{query}"
Keep your response short, warm, and helpful. If appropriate, suggest how you can help them with research or information."""
        
        response = simple_llm.call([{"role": "user", "content": prompt}])
        return response
    except Exception as e:
        print(f"[ERROR] Chitchat LLM error: {e}")
        return "Hello! I'm Check Please, your AI research assistant. How can I help you today?"

# --- Endpoints ---
@app.get("/")
def read_root():
    return {
        "status": "Check Please AI Service is running",
        "version": "0.3.0",
        "system": "Intelligent Agentic RAG with CrewAI",
        "features": [
            "Autonomous tool selection",
            "Multi-source validation (Database + SINTA + Google Scholar)",
            "Guaranteed database check first",
            "Cross-validated academic information"
        ]
    }

@app.post("/api/chat")
async def handle_chat_query(request: QueryRequest):
    """
    Intelligent agentic routing:
    - Simple chitchat → Direct LLM (fast)
    - Academic queries → Intelligent CrewAI Agent (autonomous multi-tool)
    """
    try:
        print(f"\n{'='*60}")
        print(f"[API] Received query: {request.message}")
        print(f"[API] User URLs: {request.user_urls}")
        print(f"{'='*60}")
        
        # Check if it's simple chitchat
        if not request.user_urls and is_chitchat(request.message):
            print("[API] Detected: CHITCHAT - Using simple LLM")
            result = handle_chitchat(request.message)
            print(f"[API] Chitchat response generated")
        else:
            print("[API] Detected: ACADEMIC QUERY - Using Intelligent CrewAI Agent")
            print("[API] Agent will autonomously:")
            print("[API]   1. Check database (MANDATORY)")
            print("[API]   2. Decide which tools to use (SINTA/Scholar/WebScraper)")
            print("[API]   3. Cross-validate data from multiple sources")
            print("[API]   4. Synthesize comprehensive answer")
            print(f"{'='*60}\n")
            
            result = run_agentic_rag_crew(request.message, request.user_urls)
            
            print(f"\n{'='*60}")
            print(f"[API] Agent completed! Response length: {len(str(result))} chars")
            print(f"{'='*60}")
        
        return {"response": str(result)}
        
    except Exception as e:
        print(f"\n[ERROR] Exception in /api/chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "Agent execution failed. Please try again."}
        )
