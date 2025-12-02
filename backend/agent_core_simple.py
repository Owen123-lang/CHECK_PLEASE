import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from tools import academic_search_tool, dynamic_web_scraper_tool, google_scholar_tool, sinta_scraper_tool, cv_generator_tool, ui_scholar_search_tool, pdf_search_tool
import re

load_dotenv()

class SimpleRAG:
    """
    SIMPLIFIED RAG System with 3-tier routing:
    
    TIER 1: DIRECT ANSWER (no tools)
    - Simple lists (lecturers, faculty, professors)
    - Basic facts already in database
    
    TIER 2: SINGLE TOOL USE (minimal CrewAI)
    - Specific person lookup
    - Single source verification
    
    TIER 3: MULTI-AGENT (full CrewAI)
    - Complex research queries
    - Cross-validation needed
    - Publications analysis
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        self.llm = LLM(
            model="gemini/gemini-2.0-flash",
            api_key=api_key,
            temperature=0.1,  # Lower for more deterministic output
            max_tokens=1500,
        )
    
    def query(self, user_query: str, user_urls: list = None, conversation_history: list = None) -> str:
        """
        Smart routing based on query complexity.
        """
        try:
            print("\n" + "=" * 70)
            print("🚀 SIMPLIFIED RAG QUERY PROCESSING")
            print("=" * 70)
            print(f"📝 Query: {user_query}")
            
            # STEP 1: Vector Search (always do this first)
            print("\n[STEP 1] 🔎 Vector Search...")
            vector_results = self._vector_search(user_query)
            
            # STEP 2: Detect query type and route
            query_type = self._detect_query_type(user_query)
            print(f"\n[STEP 2] 🎯 Query Type: {query_type}")
            
            if query_type == "SIMPLE_LIST":
                # TIER 1: Direct answer from RAG
                print("[TIER 1] 📋 Simple list query - Direct answer from database")
                result = self._direct_list_answer(user_query, vector_results)
                
            elif query_type == "BASIC_LOOKUP":
                # TIER 2: Single tool use
                print("[TIER 2] 🔍 Basic lookup - Minimal tool use")
                result = self._basic_lookup(user_query, vector_results)
                
            else:
                # TIER 3: Full multi-agent
                print("[TIER 3] 🤖 Complex query - Full CrewAI agents")
                result = self._complex_query(user_query, vector_results, conversation_history)
            
            # Post-processing
            print("\n[POST-PROCESSING] 🧹 Cleaning output...")
            result = self._filter_personal_info(result)
            result = self._deduplicate_gentle(result)
            
            print("\n" + "=" * 70)
            print("✅ QUERY PROCESSING COMPLETE")
            print("=" * 70)
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._emergency_fallback(user_query)
    
    def _detect_query_type(self, query: str) -> str:
        """
        Classify query into 3 tiers:
        - SIMPLE_LIST: Just list names/items from database
        - BASIC_LOOKUP: Single person/topic lookup
        - COMPLEX: Multi-step research needed
        """
        query_lower = query.lower()
        
        # TIER 1: Simple list queries
        simple_list_patterns = [
            r'\blist\s+(all|of)?\s*(the)?\s*lecturers?',
            r'\blist\s+(all|of)?\s*(the)?\s*professors?',
            r'\blist\s+(all|of)?\s*(the)?\s*faculty',
            r'\blist\s+(all|of)?\s*(the)?\s*staff',
            r'\blist\s+(all|of)?\s*(the)?\s*dosen',
            r'\bgive\s+me\s+.*\blist\b.*\blecturers?',
            r'\bshow\s+me\s+.*\blecturers?',
            r'\bsiapa\s+saja\s+dosen',
            r'\bdaftar\s+dosen',
        ]
        
        for pattern in simple_list_patterns:
            if re.search(pattern, query_lower):
                return "SIMPLE_LIST"
        
        # TIER 2: Basic lookup (specific person or simple fact)
        basic_lookup_patterns = [
            r'\bwho\s+is\b',
            r'\bsiapa\s+(itu)?\b',
            r'\btell\s+me\s+about\b',
            r'\binformation\s+about\b',
            r'\bprofile\s+of\b',
        ]
        
        # Check if query is asking about specific person (capitalized name)
        has_person_name = bool(re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', query))
        
        for pattern in basic_lookup_patterns:
            if re.search(pattern, query_lower) or has_person_name:
                return "BASIC_LOOKUP"
        
        # TIER 3: Everything else (complex)
        return "COMPLEX"
    
    def _direct_list_answer(self, query: str, vector_results: str) -> str:
        """
        TIER 1: Direct answer for simple list queries.
        NO TOOLS. Just extract and format from RAG results.
        """
        print("[TIER 1] Extracting names from database...")
        
        # Extract lecturer names from vector results
        names = set()
        
        # Pattern to match academic names with titles
        name_patterns = [
            r'((?:Prof\.?\s*)?(?:Dr\.?\s*)?(?:Ir\.?\s*)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+(?:\s*,\s*(?:S\.T\.|M\.Sc|M\.Eng|Ph\.D|MT\.|IPU\.?))*)',
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, vector_results)
            for match in matches:
                name = match.strip()
                # Validate it's a real name (not common words)
                if len(name) > 8 and 'Copyright' not in name and 'Contact' not in name:
                    names.add(name)
        
        if not names:
            return "⚠️ No lecturers found in database. Please try a different query."
        
        # Sort names alphabetically
        sorted_names = sorted(names)
        
        # Format output
        output = f"📚 **List of Lecturers ({len(sorted_names)} found)**\n\n"
        
        # Group by title
        professors = [n for n in sorted_names if 'Prof.' in n]
        doctors = [n for n in sorted_names if 'Dr.' in n and 'Prof.' not in n]
        others = [n for n in sorted_names if 'Dr.' not in n and 'Prof.' not in n]
        
        if professors:
            output += "## 🎓 Professors\n"
            for name in professors[:20]:  # Limit to 20
                output += f"• {name}\n"
            output += "\n"
        
        if doctors:
            output += "## 👨‍🏫 Doctors/Senior Lecturers\n"
            for name in doctors[:20]:
                output += f"• {name}\n"
            output += "\n"
        
        if others:
            output += "## 👨‍🎓 Lecturers\n"
            for name in others[:20]:
                output += f"• {name}\n"
            output += "\n"
        
        output += f"\n📊 **Total:** {len(sorted_names)} lecturers\n"
        output += f"💡 **Source:** Academic Database (Astra DB)\n"
        
        print(f"[TIER 1] ✓ Formatted {len(sorted_names)} unique names")
        return output
    
    def _basic_lookup(self, query: str, vector_results: str) -> str:
        """
        TIER 2: Basic lookup with minimal tool use.
        Use LLM to format RAG results nicely.
        """
        print("[TIER 2] Using LLM to format database results...")
        
        prompt = f"""You are an academic assistant. Answer this query based ONLY on the provided database information.

Query: {query}

Database Information:
{vector_results[:3000]}

Instructions:
1. Answer concisely (max 300 words)
2. Use ONLY information from the database above
3. Format nicely with markdown
4. Include: name, position, research areas (if available)
5. DO NOT make up information
6. DO NOT include personal details (birth date, family, etc.)

Answer:"""
        
        try:
            response = self.llm.call([{"role": "user", "content": prompt}])
            return str(response)
        except Exception as e:
            print(f"[TIER 2] LLM error: {e}")
            # Fallback to raw results
            return f"Based on database:\n\n{vector_results[:1000]}"
    
    def _complex_query(self, query: str, vector_results: str, conversation_history: list = None) -> str:
        """
        TIER 3: Complex query with full CrewAI multi-agent system.
        """
        print("[TIER 3] Launching full CrewAI system...")
        
        # Use existing complex agent logic
        from agent_core import HybridRAG
        hybrid_rag = HybridRAG()
        return hybrid_rag.query(query, user_urls=None, conversation_history=conversation_history)
    
    def _vector_search(self, query: str) -> str:
        """Search the Astra DB vector database."""
        try:
            result = academic_search_tool._run(query)
            print(f"  ✓ Vector search returned {len(result)} characters")
            return result
        except Exception as e:
            print(f"  ✗ Vector search failed: {e}")
            return ""
    
    def _filter_personal_info(self, text: str) -> str:
        """Remove personal information."""
        personal_keywords = [
            ('born on', 'tanggal lahir'),
            ('married to', 'menikah dengan'),
            ('has children', 'memiliki anak'),
        ]
        
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_lower = line.lower()
            is_personal = any(
                any(kw in line_lower for kw in keyword_pair)
                for keyword_pair in personal_keywords
            )
            
            if not is_personal:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _deduplicate_gentle(self, text: str) -> str:
        """Remove exact duplicate lines."""
        lines = text.split('\n')
        seen_lines = set()
        deduplicated_lines = []
        
        for line in lines:
            clean_line = line.strip()
            
            if not clean_line.startswith('•') and not clean_line.startswith('-'):
                deduplicated_lines.append(line)
                continue
            
            if clean_line not in seen_lines:
                seen_lines.add(clean_line)
                deduplicated_lines.append(line)
        
        return '\n'.join(deduplicated_lines)
    
    def _emergency_fallback(self, query: str) -> str:
        """Emergency fallback response."""
        return f"""⚠️ I encountered an error processing your request: "{query}"

Please try:
1. Rephrasing your question
2. Being more specific
3. Asking about a particular person or topic"""

# Singleton instance
_simple_rag = None

def get_simple_rag():
    global _simple_rag
    if _simple_rag is None:
        _simple_rag = SimpleRAG()
    return _simple_rag

def run_simple_rag(user_query: str, user_urls: list = None, conversation_history: list = None) -> str:
    """
    Main entry point for simplified RAG system.
    """
    simple_rag = SimpleRAG()
    return simple_rag.query(user_query, user_urls, conversation_history)
