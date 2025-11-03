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
from pdf_generator import create_cv_pdf  # Import CV generator
from datetime import datetime
import uuid

load_dotenv()

app = FastAPI(
    title="Check Please API",
    description="API for Intelligent Agentic RAG with CrewAI + AI-Powered CV Generation",
    version="0.5.0"  # Version bump for AI CV feature
)

# --- Konfigurasi CORS (DIPERBAIKI) ---
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
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

# Session storage for conversation history (in-memory, will reset on server restart)
conversation_sessions = {}

# --- Model Data Pydantic ---
class QueryRequest(BaseModel):
    message: str
    user_urls: list[str] | None = None
    session_id: str | None = None

class CVGenerationRequest(BaseModel):
    professor_name: str
    session_id: str | None = None
    use_crewai: bool = True  # New flag to enable/disable CrewAI agents

# --- Helper Functions ---
def is_chitchat(query: str) -> bool:
    """
    Determine if a query is simple chitchat or requires RAG.
    """
    query_lower = query.lower().strip()
    
    chitchat_keywords = [
        'halo', 'hai', 'hello', 'hi', 'hey',
        'selamat pagi', 'selamat siang', 'selamat malam',
        'good morning', 'good afternoon', 'good evening',
        'apa kabar', 'how are you',
        'test', 'testing', 'tes',
        'terima kasih', 'thank you', 'thanks',
        'bye', 'goodbye', 'sampai jumpa'
    ]
    
    if len(query_lower.split()) <= 3:
        for keyword in chitchat_keywords:
            if keyword in query_lower:
                return True
    
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

def store_conversation(session_id: str, user_message: str, ai_response: str):
    """Store conversation in session for CV generation context."""
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = []
    
    conversation_sessions[session_id].append({
        "timestamp": datetime.now().isoformat(),
        "user": user_message,
        "assistant": ai_response
    })
    
    if len(conversation_sessions[session_id]) > 10:
        conversation_sessions[session_id] = conversation_sessions[session_id][-10:]

def get_conversation_context(session_id: str) -> str:
    """Get conversation history as text for CV generation."""
    if session_id not in conversation_sessions:
        return ""
    
    context = "=== CONVERSATION HISTORY ===\n\n"
    for msg in conversation_sessions[session_id]:
        context += f"User: {msg['user']}\n"
        context += f"Assistant: {msg['assistant'][:500]}...\n\n"
    
    return context

# --- Endpoints ---
@app.get("/")
def read_root():
    return {
        "status": "Check Please AI Service is running",
        "version": "0.5.0",
        "system": "Intelligent Agentic RAG with CrewAI + AI-Powered CV Generation",
        "features": [
            "Autonomous tool selection",
            "Multi-source validation (Database + SINTA + Google Scholar)",
            "Guaranteed database check first",
            "Cross-validated academic information",
            "AI-Powered CV Generation with multi-agent system",
            "Comprehensive data collection from 4+ sources"
        ]
    }

@app.post("/api/chat")
async def handle_chat_query(request: QueryRequest):
    """
    Intelligent agentic routing with conversation tracking for CV generation.
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        print(f"\n{'='*60}")
        print(f"[API] Session ID: {session_id}")
        print(f"[API] Received query: {request.message}")
        print(f"[API] User URLs: {request.user_urls}")
        print(f"{'='*60}")
        
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
        
        store_conversation(session_id, request.message, str(result))
        
        return {
            "response": str(result),
            "session_id": session_id
        }
        
    except Exception as e:
        print(f"\n[ERROR] Exception in /api/chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "Agent execution failed. Please try again."}
        )

@app.post("/api/generate-cv")
async def generate_cv(request: CVGenerationRequest):
    """
    Generate a professional CV PDF using AI agents for data collection.
    
    NEW FEATURE: Uses CrewAI multi-agent system to:
    1. Collect data from database, SINTA, Google Scholar, and web
    2. Analyze and structure the information
    3. Compose a professional CV document
    4. Generate PDF with comprehensive details
    """
    try:
        print(f"\n{'='*60}")
        print(f"[CV API] 🤖 AI-POWERED CV GENERATION for: {request.professor_name}")
        print(f"[CV API] Session ID: {request.session_id}")
        print(f"[CV API] Using CrewAI: {request.use_crewai}")
        print(f"{'='*60}")
        
        # Get conversation context if available
        conversation_context = ""
        if request.session_id:
            conversation_context = get_conversation_context(request.session_id)
            print(f"[CV API] Using conversation context: {len(conversation_context)} chars")
        
        # Choose generation method
        if request.use_crewai:
            # NEW: Use CrewAI multi-agent system
            print("[CV API] 🚀 Launching CrewAI Multi-Agent System...")
            print("[CV API]   Agent 1: Data Collector (searches all sources)")
            print("[CV API]   Agent 2: Data Analyzer (extracts structured info)")
            print("[CV API]   Agent 3: CV Composer (formats professional CV)")
            
            from cv_agent import generate_cv_with_agents
            
            cv_result = generate_cv_with_agents(
                professor_name=request.professor_name,
                session_id=request.session_id
            )
            
            if not cv_result["success"]:
                raise Exception(cv_result.get("error", "CV generation failed"))
            
            cv_data = cv_result["cv_text"]
            
            print(f"[CV API] ✓ CrewAI completed!")
            
            # Safely access metadata fields (they may not exist in simplified version)
            metadata = cv_result.get("metadata", {})
            if "agents_used" in metadata:
                print(f"[CV API]   - Agents used: {', '.join(metadata['agents_used'])}")
            if "character_count" in metadata:
                print(f"[CV API]   - Data collected: {metadata['character_count']} chars")
            if "sources_used" in metadata:
                print(f"[CV API]   - Sources used: {', '.join(metadata['sources_used'])}")
            if "generated_by" in metadata:
                print(f"[CV API]   - Generated by: {metadata['generated_by']}")
            
        else:
            # FALLBACK: Use simple tool-based collection
            print("[CV API] Using simple tool-based collection...")
            from tools import cv_generator_tool
            cv_data = cv_generator_tool._run(request.professor_name)
        
        # Add conversation context
        if conversation_context:
            cv_data = conversation_context + "\n\n" + cv_data
        
        # Generate PDF
        print("[CV API] 📄 Generating PDF document...")
        pdf_bytes = create_cv_pdf(cv_data, conversation_context)
        
        print(f"[CV API] PDF generated: {len(pdf_bytes)} bytes")
        
        # Prepare filename
        safe_name = request.professor_name.replace(" ", "_").replace(".", "")
        filename = f"CV_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        print(f"[CV API] ✅ SUCCESS! Filename: {filename}")
        print(f"{'='*60}\n")
        
        # Return PDF as downloadable file
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        print(f"\n[ERROR] CV Generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "CV generation failed. Please ensure the professor name is correct and try again."
            }
        )

@app.post("/api/generate-pdf")
async def generate_pdf(request: QueryRequest):
    """
    Generate a simple PDF report from chat response.
    """
    try:
        print(f"\n{'='*60}")
        print(f"[PDF API] Generating PDF report")
        print(f"[PDF API] Message: {request.message[:100]}...")
        print(f"{'='*60}")
        
        from pdf_generator import create_profile_pdf
        
        pdf_bytes = create_profile_pdf(request.message)
        
        print(f"[PDF API] PDF generated: {len(pdf_bytes)} bytes")
        
        filename = f"CheckPlease_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        print(f"[PDF API] ✓ Success! Filename: {filename}")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        print(f"\n[ERROR] PDF Generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "PDF generation failed. Please try again."
            }
        )

@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session conversation history."""
    if session_id not in conversation_sessions:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )
    
    return {
        "session_id": session_id,
        "message_count": len(conversation_sessions[session_id]),
        "messages": conversation_sessions[session_id]
    }
