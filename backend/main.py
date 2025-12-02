from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agent_core import run_agentic_rag_crew  # Full CrewAI agent
from agent_core_simple import run_simple_rag  # Simplified routing system
from starlette.responses import StreamingResponse, Response
from crewai import LLM
import io
import os
from dotenv import load_dotenv
from pdf_generator import create_cv_pdf  # Import CV generator
from datetime import datetime
import uuid
from typing import Optional, List
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from astrapy import DataAPIClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

app = FastAPI(
    title="Check Please API",
    description="API for Intelligent Agentic RAG with CrewAI + AI-Powered CV Generation",
    version="0.5.0"  # Version bump for AI CV feature
)

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    message: str
    user_urls: Optional[List[str]] = None
    session_id: Optional[str] = None

class CVGenerationRequest(BaseModel):
    professor_name: str
    session_id: Optional[str] = None
    use_crewai: bool = True

# --- Konfigurasi CORS (DIPERBAIKI) ---
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://check-please-gray.vercel.app",
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
    model="gemini/gemini-2.5-pro",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)

# Session storage for conversation history (in-memory, will reset on server restart)
conversation_sessions = {}

# --- Helper Functions ---

def format_response_for_frontend(text: str) -> str:
    """
    Convert markdown-formatted response to clean HTML for better frontend display.
    Removes markdown syntax and applies proper HTML formatting.
    """
    import re
    
    # Remove excessive markdown symbols
    formatted = text
    
    # Convert headers
    formatted = re.sub(r'^# (.+)$', r'<h1 class="text-2xl font-bold text-gray-900 mb-4">\1</h1>', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^## (.+)$', r'<h2 class="text-xl font-semibold text-red-700 mt-6 mb-3">\1</h2>', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^### (.+)$', r'<h3 class="text-lg font-medium text-gray-800 mt-4 mb-2">\1</h3>', formatted, flags=re.MULTILINE)
    
    # Convert bold text
    formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong class="font-semibold text-gray-900">\1</strong>', formatted)
    
    # Convert bullet points
    formatted = re.sub(r'^- (.+)$', r'<li class="ml-4 mb-2">\1</li>', formatted, flags=re.MULTILINE)
    
    # Convert numbered lists (preserve numbers)
    formatted = re.sub(r'^(\d+)\. (.+)$', r'<li class="ml-4 mb-3" value="\1">\2</li>', formatted, flags=re.MULTILINE)
    
    # Convert emoji icons to styled spans
    formatted = re.sub(r'📚', '<span class="text-blue-600">📚</span>', formatted)
    formatted = re.sub(r'📊', '<span class="text-green-600">📊</span>', formatted)
    formatted = re.sub(r'🔗', '<span class="text-indigo-600">🔗</span>', formatted)
    formatted = re.sub(r'👥', '<span class="text-purple-600">👥</span>', formatted)
    
    # Wrap consecutive <li> tags in <ul> or <ol>
    # Find numbered list items
    formatted = re.sub(r'(<li class="ml-4 mb-3" value="\d+">.+?</li>(?:\s*<li class="ml-4 mb-3" value="\d+">.+?</li>)*)', 
                      r'<ol class="list-decimal list-inside space-y-2 mb-4">\1</ol>', formatted, flags=re.DOTALL)
    
    # Find bullet list items
    formatted = re.sub(r'(<li class="ml-4 mb-2">.+?</li>(?:\s*<li class="ml-4 mb-2">.+?</li>)*)', 
                      r'<ul class="list-disc list-inside space-y-1 mb-4">\1</ul>', formatted, flags=re.DOTALL)
    
    # Convert horizontal rules
    formatted = re.sub(r'^---+$', '<hr class="my-6 border-t-2 border-gray-300" />', formatted, flags=re.MULTILINE)
    
    # Wrap paragraphs (text without HTML tags)
    lines = formatted.split('\n')
    result_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line is already wrapped in HTML tag
        if line.startswith('<'):
            result_lines.append(line)
        else:
            # It's a plain text paragraph
            result_lines.append(f'<p class="mb-3 text-gray-700 leading-relaxed">{line}</p>')
    
    formatted = '\n'.join(result_lines)
    
    # Wrap entire response in a container div
    formatted = f'<div class="formatted-response prose max-w-none">{formatted}</div>'
    
    return formatted

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
        
        # Get conversation history for context
        conversation_history = conversation_sessions.get(session_id, [])
        if conversation_history:
            print(f"[API] Using {len(conversation_history)} previous messages for context")
        
        print(f"{'='*60}")
        
        if not request.user_urls and is_chitchat(request.message):
            print("[API] Detected: CHITCHAT - Using simple LLM")
            result = handle_chitchat(request.message)
            print(f"[API] Chitchat response generated")
        else:
            print("[API] Detected: ACADEMIC QUERY - Using Smart Routing System")
            print("[API] System will:")
            print("[API]   • TIER 1: Direct answer for simple lists (no tools)")
            print("[API]   • TIER 2: Single tool for basic lookups")
            print("[API]   • TIER 3: Full CrewAI for complex queries")
            print(f"{'='*60}\n")
            
            # Use simplified routing system for better efficiency (with session_id for PDF search)
            result = run_simple_rag(request.message, request.user_urls, conversation_history, session_id)
            
            print(f"\n{'='*60}")
            print(f"[API] Agent completed! Response length: {len(str(result))} chars")
            print(f"{'='*60}")
        
        store_conversation(session_id, request.message, str(result))
        
        # Format response untuk frontend (convert markdown to HTML)
        formatted_result = format_response_for_frontend(str(result))
        
        return {
            "response": formatted_result,
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

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), session_id: str = None):
    """
    Upload and process a PDF file. Extracts text, chunks it, and stores in vector database.
    
    This allows users to upload their own PDF documents and ask questions about them.
    The AI will use the User PDF Search Tool to answer questions based on uploaded content.
    """
    try:
        print(f"\n{'='*60}")
        print(f"[PDF UPLOAD] Processing file: {file.filename}")
        print(f"[PDF UPLOAD] Content type: {file.content_type}")
        print(f"[PDF UPLOAD] Session ID: {session_id}")
        print(f"{'='*60}")
        
        # Validate file type
        if not file.filename.endswith('.pdf'):
            return JSONResponse(
                status_code=400,
                content={"error": "Only PDF files are allowed"}
            )
        
        # Read PDF content
        pdf_bytes = await file.read()
        print(f"[PDF UPLOAD] File size: {len(pdf_bytes)} bytes")
        
        # Extract text from PDF
        print("[PDF UPLOAD] Extracting text from PDF...")
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(pdf_reader.pages)
        print(f"[PDF UPLOAD] PDF has {num_pages} pages")
        
        extracted_text = []
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text = page.extract_text()
            if text.strip():
                extracted_text.append({
                    'page': page_num,
                    'text': text
                })
                print(f"[PDF UPLOAD]   Page {page_num}: {len(text)} characters")
        
        if not extracted_text:
            return JSONResponse(
                status_code=400,
                content={"error": "Could not extract text from PDF. The PDF might be image-based or encrypted."}
            )
        
        total_chars = sum(len(item['text']) for item in extracted_text)
        print(f"[PDF UPLOAD] Total extracted: {total_chars} characters from {len(extracted_text)} pages")
        
        # Chunk the text for better search
        print("[PDF UPLOAD] Chunking text...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = []
        for item in extracted_text:
            page_chunks = text_splitter.split_text(item['text'])
            for chunk_text in page_chunks:
                chunks.append({
                    'text': chunk_text,
                    'page': item['page'],
                    'pdf_name': file.filename
                })
        
        print(f"[PDF UPLOAD] Created {len(chunks)} chunks")
        
        # Initialize embedding model
        print("[PDF UPLOAD] Generating embeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        # Connect to Astra DB
        client = DataAPIClient(os.getenv("ASTRA_DB_APPLICATION_TOKEN"))
        db = client.get_database_by_api_endpoint(os.getenv("ASTRA_DB_API_ENDPOINT"))
        collection = db.get_collection(os.getenv("ASTRA_DB_COLLECTION", "academic_profiles_ui"))
        
        # Store chunks in database with embeddings
        print("[PDF UPLOAD] Storing in vector database...")
        stored_count = 0
        
        for i, chunk in enumerate(chunks):
            try:
                # Generate embedding for this chunk
                embedding = embeddings.embed_query(chunk['text'])
                
                # Generate unique ID using UUID + timestamp to avoid collisions
                unique_id = f"{session_id or 'default'}_{uuid.uuid4().hex[:12]}_{i}"
                
                # Create document
                doc = {
                    "_id": unique_id,
                    "text": chunk['text'],
                    "page_number": chunk['page'],
                    "pdf_name": chunk['pdf_name'],
                    "source_type": "user_pdf",
                    "session_id": session_id,
                    "uploaded_at": datetime.now().isoformat(),
                    "$vector": embedding
                }
                
                # Use insert_one with error handling for duplicates
                try:
                    collection.insert_one(doc)
                    stored_count += 1
                    
                    if (i + 1) % 10 == 0:
                        print(f"[PDF UPLOAD]   Stored {i + 1}/{len(chunks)} chunks...")
                except Exception as insert_error:
                    # If document exists, try with new UUID
                    if "DOCUMENT_ALREADY_EXISTS" in str(insert_error):
                        doc["_id"] = f"{session_id or 'default'}_{uuid.uuid4().hex[:12]}_{i}_{int(datetime.now().timestamp())}"
                        collection.insert_one(doc)
                        stored_count += 1
                        print(f"[PDF UPLOAD]   Retried chunk {i} with new ID")
                    else:
                        raise insert_error
                    
            except Exception as e:
                print(f"[PDF UPLOAD] Error storing chunk {i}: {e}")
                continue
        
        print(f"[PDF UPLOAD] ✅ Successfully stored {stored_count}/{len(chunks)} chunks")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "filename": file.filename,
            "pages": num_pages,
            "chunks_stored": stored_count,
            "total_characters": total_chars,
            "message": f"PDF '{file.filename}' uploaded successfully! You can now ask questions about it.",
            "session_id": session_id
        }
        
    except Exception as e:
        print(f"\n[ERROR] PDF Upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "message": "Failed to process PDF. Please try again with a different file."
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
