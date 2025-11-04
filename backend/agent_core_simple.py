import os
from dotenv import load_dotenv
from crewai import LLM
from tools import (
    academic_search_tool, 
    dynamic_web_scraper_tool, 
    google_scholar_tool,
    google_scholar_profiles_tool,
    google_scholar_author_tool,
    google_scholar_publications_tool,
    google_scholar_cited_by_tool,
    sinta_scraper_tool,
    web_search_tool
)
import re

load_dotenv()

class SimpleRAG:
    """Simplified RAG system with guaranteed database check and fallback."""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        self.llm = LLM(
            model="gemini/gemini-2.0-flash",
            api_key=api_key,
            temperature=0.3,
            max_tokens=4000,
        )
    
    def query(self, user_query: str, user_urls: list[str] = None, conversation_history: list[dict] = None) -> str:
        """
        Main RAG query method with GUARANTEED steps:
        1. ALWAYS check database first
        2. If insufficient, scrape UI website
        3. Format with LLM
        
        Args:
            user_query: The current user query
            user_urls: Optional list of URLs to scrape
            conversation_history: List of previous messages [{"user": "...", "assistant": "..."}]
        """
        print("\n" + "="*60)
        print(f"[SIMPLE RAG] Processing query: {user_query}")
        if conversation_history:
            print(f"[SIMPLE RAG] Using conversation history: {len(conversation_history)} messages")
        print("="*60)
        
        all_context = []
        
        # Add conversation context to help resolve pronouns
        context_summary = ""
        if conversation_history and len(conversation_history) > 0:
            context_summary = self._build_context_summary(conversation_history)
            print(f"[CONTEXT] Previous conversation about: {context_summary}")
        
        # ============================================
        # STEP 1: ALWAYS CHECK DATABASE FIRST
        # ============================================
        print("\n[STEP 1/4] Checking database...")
        try:
            # Enhance query with context if needed
            enhanced_query = self._enhance_query_with_context(user_query, context_summary)
            print(f"  → Enhanced query: {enhanced_query}")
            
            db_result = academic_search_tool._run(enhanced_query)
            
            # Validate database result
            if self._is_valid_data(db_result):
                print("  ✓ Database has valid data!")
                all_context.append(f"Database Info:\n{db_result[:2000]}")
            else:
                print("  ✗ Database returned invalid/corrupt data")
        except Exception as e:
            print(f"  ✗ Database error: {e}")
        
        # ============================================
        # STEP 2: SCRAPE UI WEBSITE (GUARANTEED DATA)
        # ============================================
        print("\n[STEP 2/4] Scraping UI official website...")
        try:
            ui_url = "https://ee.ui.ac.id/staff-pengajar/"
            print(f"  → Scraping: {ui_url}")
            web_result = dynamic_web_scraper_tool._run(ui_url)
            
            if self._is_valid_data(web_result):
                print("  ✓ Website scraping successful!")
                all_context.append(f"UI Website Data:\n{web_result[:2000]}")
            else:
                print("  ✗ Website returned invalid data")
        except Exception as e:
            print(f"  ✗ Website scraping error: {e}")
        
        # ============================================
        # STEP 3: USER-PROVIDED URLS (if any)
        # ============================================
        if user_urls and len(user_urls) > 0:
            print(f"\n[STEP 3/4] Scraping user-provided URLs: {len(user_urls)}")
            for url in user_urls[:3]:  # Limit to 3 URLs
                try:
                    print(f"  → Scraping: {url}")
                    url_result = dynamic_web_scraper_tool._run(url)
                    if self._is_valid_data(url_result):
                        all_context.append(f"User URL ({url}):\n{url_result[:1000]}")
                        print("    ✓ Success")
                except Exception as e:
                    print(f"    ✗ Error: {e}")
        
        # ============================================
        # STEP 4: LLM SYNTHESIS
        # ============================================
        print("\n[STEP 4/4] Synthesizing answer with LLM...")
        
        if not all_context:
            print("  ✗ NO DATA COLLECTED! Using emergency response.")
            return self._emergency_response(user_query)
        
        # Combine all context
        combined_context = "\n\n---\n\n".join(all_context)
        print(f"  → Total context: {len(combined_context)} characters")
        
        # Determine query intent
        intent = self._detect_intent(user_query)
        print(f"  → Query intent: {intent}")
        
        # Generate response
        try:
            response = self._generate_response(user_query, combined_context, intent, conversation_history)
            print("  ✓ Response generated successfully!")
            return response
        except Exception as e:
            print(f"  ✗ LLM error: {e}")
            return self._emergency_response(user_query)
    
    def _build_context_summary(self, conversation_history: list[dict]) -> str:
        """Extract key entities (names) from conversation history."""
        context = ""
        
        # Get the last few messages
        recent_messages = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
        
        for msg in recent_messages:
            user_msg = msg.get("user", "")
            assistant_msg = msg.get("assistant", "")
            
            # Extract names (capitalize words, likely names)
            import re
            names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', user_msg + " " + assistant_msg)
            
            # Filter academic titles
            academic_names = [n for n in names if not n in ["Database", "Website", "Info", "Research"]]
            
            if academic_names:
                context = ", ".join(set(academic_names))
        
        return context
    
    def _enhance_query_with_context(self, query: str, context_summary: str) -> str:
        """
        Enhance query with context to resolve pronouns.
        Example: "what are his research?" + context "Alfan Praseka" -> "Alfan Praseka research"
        """
        query_lower = query.lower()
        
        # Check if query contains pronouns
        pronouns = ["his", "her", "their", "he", "she", "they", "him"]
        has_pronoun = any(pronoun in query_lower.split() for pronoun in pronouns)
        
        if has_pronoun and context_summary:
            # Replace pronoun with context
            print(f"  → Detected pronoun in query, adding context: {context_summary}")
            return f"{context_summary} {query}"
        
        return query
    
    def _is_valid_data(self, data: str) -> bool:
        """Check if data is valid (not error pages or garbage)."""
        if not data or len(data) < 100:
            return False
        
        # Check for error indicators
        error_indicators = [
            '<!DOCTYPE html>',
            '<div class="error-container">',
            '404',
            'An error occurred while processing'
        ]
        
        error_count = sum(1 for indicator in error_indicators if indicator in data)
        if error_count > 2:
            return False
        
        # Check for academic content
        valid_indicators = ['prof', 'dr.', 'dosen', 'lecture', 'departemen']
        valid_count = sum(1 for indicator in valid_indicators if indicator.lower() in data.lower())
        
        return valid_count >= 2
    
    def _detect_intent(self, query: str) -> str:
        """Detect what user wants."""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ['list', 'daftar', 'siapa saja', 'semua']):
            return 'list'
        elif any(kw in query_lower for kw in ['profil lengkap', 'detail', 'comprehensive']):
            return 'full_profile'
        elif any(kw in query_lower for kw in ['penelitian', 'publikasi', 'research']):
            return 'research'
        else:
            return 'general'
    
    def _generate_response(self, query: str, context: str, intent: str, conversation_history: list[dict] = None) -> str:
        """Generate natural response using LLM with conversation awareness."""
        
        # Build conversation context string
        conversation_context = ""
        if conversation_history:
            conversation_context = "\n\nPrevious Conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages
                conversation_context += f"User: {msg.get('user', '')}\n"
                conversation_context += f"Assistant: {msg.get('assistant', '')[:200]}...\n\n"
        
        if intent == 'list':
            instruction = """Extract and list all professors and lecturers mentioned.
Format:
# Daftar Dosen Departemen Teknik Elektro UI

**Profesor:**
- Prof. Dr. [Name]
- Prof. Dr. [Name]

**Lektor Kepala/Dosen:**
- Dr. [Name]
- Dr. [Name]

ONLY list names and titles. NO links, NO extra details."""
        
        elif intent == 'full_profile':
            instruction = """Extract complete ACADEMIC and PROFESSIONAL profile ONLY.

**INCLUDE:**
- Academic degrees (S1, S2, S3, PhD)
- Professional positions (Professor, Lecturer, Chairperson)
- Research areas and interests
- Publications and citations
- SINTA score, Scopus ID, Google Scholar
- Academic awards and recognitions
- Professional affiliations

**NEVER INCLUDE:**
- Birth date, age, personal life
- Family members, spouse, children
- Hobbies or personal interests

Format professionally in markdown. Skip any personal information completely."""
        
        elif intent == 'research':
            instruction = """Focus on research activities, publications, and citations.
Present in structured format with key achievements.
ONLY academic and professional information."""
        
        else:
            instruction = """Provide a clear, concise answer to the query.
Format professionally and naturally.
ONLY include academic and professional information.
NEVER include personal life details (family, birth date, etc.)."""
        
        prompt = f"""You are an academic information assistant with conversation memory.

{conversation_context}

User Query: "{query}"

Context Data:
{context[:3500]}

Instructions:
{instruction}

IMPORTANT:
- If the user uses pronouns like "his", "her", "their", refer to the person mentioned in the previous conversation
- Extract ONLY factual ACADEMIC and PROFESSIONAL information from the context
- NEVER include personal information: birth date, family, spouse, children, personal life
- Ignore navigation menus, error messages, and irrelevant text
- If asking for a list, ONLY provide names and titles
- If asking for details, include all relevant ACADEMIC information
- Be natural and conversational
- Use proper markdown formatting
- MAINTAIN CONTEXT: If the previous query was about a specific person and the current query uses "his/her", refer to that same person

Answer:"""
        
        response = self.llm.call([{"role": "user", "content": prompt}])
        
        # Filter out personal information
        filtered_response = self._filter_personal_info(str(response))
        
        return filtered_response
    
    def _filter_personal_info(self, text: str) -> str:
        """Remove any personal information from the response."""
        # Keywords to detect personal info lines
        personal_keywords = [
            'born on', 'lahir', 'birth', 'tanggal lahir',
            'married', 'menikah', 'istri', 'suami', 'wife', 'husband', 'spouse',
            'children', 'anak', 'son', 'daughter', 'putra', 'putri',
            'family', 'keluarga', 'personal life', 'kehidupan pribadi',
            'hobbies', 'hobby', 'hobi', 'born in', 'age'
        ]
        
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if line contains personal info
            has_personal = any(keyword in line_lower for keyword in personal_keywords)
            
            if not has_personal:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _emergency_response(self, query: str) -> str:
        """Emergency response when everything fails."""
        return f"""# Informasi Dosen Teknik Elektro UI

Mohon maaf, saya mengalami kesulitan teknis saat mengakses data.

**Silakan kunjungi langsung:**
- Website Resmi: https://ee.ui.ac.id/staff-pengajar/
- SINTA UI: https://sinta.kemdikbud.go.id/affiliations/detail?id=147

**Atau coba pertanyaan lain:**
- "siapa Prof. Riri Fitri Sari?"
- "daftar profesor di Teknik Elektro UI"

Saya akan mencoba lagi dalam beberapa saat."""

# Initialize global instance
_rag_instance = None

def get_rag_instance():
    """Get or create RAG instance (singleton pattern)."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = SimpleRAG()
    return _rag_instance

def run_agentic_rag_crew(query: str, user_urls: list[str] | None = None):
    """
    Main entry point for RAG queries.
    This replaces the complex CrewAI agent with simple, reliable RAG.
    """
    try:
        rag = get_rag_instance()
        return rag.query(query, user_urls)
    except Exception as e:
        print(f"[CRITICAL ERROR] RAG system failed: {e}")
        import traceback
        traceback.print_exc()
        return f"""# System Error

Terjadi kesalahan sistem: {str(e)}

**Informasi manual:**
- Website: https://ee.ui.ac.id/staff-pengajar/
- SINTA: https://sinta.kemdikbud.go.id

Silakan coba lagi atau kunjungi link di atas."""
