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
            model="gemini/gemini-1.5-pro",
            api_key=api_key,
            temperature=0.1,  # Lower for more deterministic output
            max_tokens=2000,  # Pro has better capacity
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
                # Use TIER 2 for list queries (LLM formatting is more reliable than regex)
                print("[TIER 2] 📋 Simple list query - Using LLM to format database results")
                result = self._basic_lookup(user_query, vector_results)
                
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
        
        # Extract lecturer names - SIMPLIFIED APPROACH
        # Data format: "Name., Degree. NextName., Degree."
        names = set()
        
        # Clean text
        text = vector_results.replace('\n---\n', ' ')
        text = vector_results.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        
        # Simple pattern: Match everything from capital letter to period before next capital
        # Matches: "Ekadiyanto., S.T., M.Sc." or "Dr. Abdul Muis., ST., M.Eng."
        pattern = r'([A-Z](?:[a-z]+|r\.|rof\.)\s+(?:[A-Z]\.?\s+)*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*[^A-Z\n]+)?\.)'
        
        matches = re.findall(pattern, text)
        
        print(f"[TIER 1] Found {len(matches)} raw matches")
        
        for idx, match in enumerate(matches[:5]):  # Debug: show first 5
            print(f"[TIER 1 DEBUG] Match {idx+1}: '{match[:80]}...' (len={len(match)})")
        
        for match in matches:
            match = match.strip()
            
            # Skip if it's a noise word
            if any(noise in match for noise in ['LECTURER', 'PROFESSOR', 'ASSISTANT', 'ASSOCIATE', 'EMERITUS', 'ADJUNCT']):
                print(f"[TIER 1 SKIP] Noise word: {match[:40]}")
                continue
            
            # Relaxed validation: just need comma (indicates degree)
            if ',' in match and len(match) > 10:
                names.add(match)
            else:
                print(f"[TIER 1 SKIP] No comma or too short: {match[:40]}")
        
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
            output += "## 🎓 Professors\n\n"
            for name in professors[:30]:  # Show up to 30
                output += f"- {name}\n"
            if len(professors) > 30:
                output += f"\n*... and {len(professors) - 30} more professors*\n"
            output += "\n"
        
        if doctors:
            output += "## 👨‍🏫 Doctors & Senior Lecturers\n\n"
            for name in doctors[:30]:
                output += f"- {name}\n"
            if len(doctors) > 30:
                output += f"\n*... and {len(doctors) - 30} more doctors*\n"
            output += "\n"
        
        if others:
            output += "## 👨‍🎓 Lecturers & Instructors\n\n"
            for name in others[:30]:
                output += f"- {name}\n"
            if len(others) > 30:
                output += f"\n*... and {len(others) - 30} more lecturers*\n"
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
        
        # Check if this is a list query
        query_lower = query.lower()
        is_list_query = any(keyword in query_lower for keyword in ['list', 'all', 'daftar', 'semua'])
        
        if is_list_query:
            prompt = f"""Extract and list ALL lecturer names from the database information below.

Query: {query}

Database Information:
{vector_results}

CRITICAL INSTRUCTIONS:
1. Extract COMPLETE names only (e.g., "Dr. Abdul Muis., ST., M.Eng.")
2. Skip INCOMPLETE names (e.g., "F. Astha" without full name)
3. Remove EXACT duplicates (e.g., if "Tomy Abuzairi" and "Abuzairi" both appear, keep only the longer one)
4. Format as a clean numbered list
5. Group by academic title: Professors (Prof.) first, then Doctors (Dr.), then Lecturers
6. DO NOT add position or research areas - NAMES ONLY
7. DO NOT include partial names, truncated names, or incomplete entries

Output format:
## Professors
1. [Full name with all titles and degrees]
2. [Full name with all titles and degrees]

## Doctors & Senior Lecturers
1. [Full name with all titles and degrees]

## Lecturers
1. [Full name with all titles and degrees]

Extract names now:"""
        else:
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
    
    def _is_valid_name(self, name: str) -> bool:
        """Validate if extracted text is a real academic name."""
        # Must have minimum length
        if len(name) < 10:
            return False
        
        # Filter out noise words
        noise_words = ['Copyright', 'Contact', 'Email', 'LECTURER', 'PROFESSOR',
                      'STAFF', 'Keahlian', 'Phone', 'Office', 'Website', 'EMERITUS',
                      'ADJUNCT', 'ASSISTANT']
        if any(word in name for word in noise_words):
            return False
        
        # Must have at least 2 word parts (first + last name)
        words = name.replace(',', ' ').split()
        # Filter out title words
        name_words = [w for w in words if w not in ['Prof.', 'Dr.', 'Ir.', 'dr.', '-Ing.']]
        if len(name_words) < 2:
            return False
        
        # Must contain uppercase letters (names)
        if not any(c.isupper() for c in name):
            return False
        
        return True
    
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
