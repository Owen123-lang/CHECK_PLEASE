import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from tools import academic_search_tool, dynamic_web_scraper_tool, google_scholar_tool, sinta_scraper_tool
import re
from collections import OrderedDict

load_dotenv()

class HybridRAG:
    """
    HYBRID RAG System:
    - Simple queries (lists) → DIRECT execution (NO CrewAI!)
    - Complex queries → CrewAI with strict limits
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        self.llm = LLM(
            model="gemini/gemini-2.0-flash",
            api_key=api_key,
            temperature=0.2,
            max_tokens=2000,
        )
    
    def query(self, user_query: str, user_urls: list = None) -> str:
        """Main entry point with intelligent routing."""
        print("\n" + "="*70)
        print("🎯 HYBRID RAG SYSTEM")
        print("="*70)
        print(f"Query: {user_query}")
        
        is_simple = self._is_simple_list_query(user_query)
        
        if is_simple:
            print("[ROUTING] SIMPLE LIST → Direct Execution (NO CrewAI)")
            return self._direct_simple_list(user_query)
        else:
            print("[ROUTING] COMPLEX QUERY → CrewAI Agent")
            return self._crewai_complex_query(user_query, user_urls)
    
    def _is_simple_list_query(self, query: str) -> bool:
        """Detect if query is just asking for a simple list."""
        query_lower = query.lower()
        
        simple_keywords = [
            'list', 'daftar', 'siapa saja', 'give me a list',
            'nama-nama', 'names of', 'who are the'
        ]
        
        complex_keywords = [
            'profil lengkap', 'complete profile', 'detail',
            'penelitian', 'research', 'publikasi', 'citation',
            'compare', 'bandingkan', 'verify', 'validasi'
        ]
        
        has_simple = any(kw in query_lower for kw in simple_keywords)
        has_complex = any(kw in query_lower for kw in complex_keywords)
        
        return has_simple and not has_complex
    
    def _direct_simple_list(self, query: str) -> str:
        """DIRECT execution for simple list queries. Bypasses CrewAI completely."""
        print("\n[DIRECT MODE] Step-by-step execution:")
        
        # Step 1: Check database
        print("[1/3] Checking database...")
        try:
            db_result = academic_search_tool._run(query)
            print(f"  ✓ Database returned {len(db_result)} characters")
            print(f"  [DEBUG] Database preview: {db_result[:300]}...")  # DEBUG
        except Exception as e:
            print(f"  ✗ Database error: {e}")
            db_result = ""
        
        # Step 2: Scrape UI website
        print("[2/3] Scraping UI website...")
        try:
            web_result = dynamic_web_scraper_tool._run("https://ee.ui.ac.id/staff-pengajar/")
            print(f"  ✓ Website returned {len(web_result)} characters")
            print(f"  [DEBUG] Website preview: {web_result[:300]}...")  # DEBUG
        except Exception as e:
            print(f"  ✗ Website error: {e}")
            web_result = ""
        
        # Combine context - INCREASED from 2000 to 3000
        combined_context = f"Database:\n{db_result[:3000]}\n\nWebsite:\n{web_result[:3000]}"
        
        print(f"  [DEBUG] Combined context length: {len(combined_context)} characters")  # DEBUG
        
        # Detect language preference
        query_lower = query.lower()
        use_indonesian = any(kw in query_lower for kw in ['daftar', 'siapa saja', 'berikan', 'tolong', 'bisa'])
        
        # Step 3: LLM extraction with IMPROVED instructions
        print(f"[3/3] Extracting names with LLM (Language: {'Indonesian' if use_indonesian else 'English'})...")
        
        if use_indonesian:
            extraction_prompt = f"""Ekstrak SEMUA nama dosen dan profesor dari data ini.

Permintaan user: "{query}"

Data yang tersedia:
{combined_context}

**ATURAN PENTING:**
1. Ekstrak SEMUA nama dosen/profesor yang ditemukan (Prof., Dr., Ir., dll.)
2. ABAIKAN: Menu navigasi ("Program Studi", "Laboratorium", "Riset", dll.)
3. TIDAK BOLEH ADA DUPLIKAT - setiap nama hanya muncul SEKALI
4. Kelompokkan berdasarkan jabatan:
   - Profesor (Prof. Dr. / Prof. Ir. / Prof.)
   - Lektor Kepala / Doktor (Dr. / Ir.)
   - Dosen (yang tidak punya gelar Prof/Dr)
5. Format: Numbering (1., 2., 3., ...) untuk mudah dibaca
6. WAJIB: Extract minimal 20 nama! Jika tidak ada 20 nama, extract semua yang tersedia.

**FORMAT OUTPUT (SIMPLE & CLEAN - NO EMOJI!):**

DAFTAR DOSEN DEPARTEMEN TEKNIK ELEKTRO UI

PROFESOR:
1. Prof. Dr. Ir. [Nama Lengkap dengan gelar]
2. Prof. Dr. [Nama Lengkap dengan gelar]
3. Prof. Ir. [Nama Lengkap dengan gelar]
(dan seterusnya...)

LEKTOR KEPALA & DOKTOR:
1. Dr. Eng. [Nama Lengkap dengan gelar]
2. Dr. Ir. [Nama Lengkap dengan gelar]
3. Dr. [Nama Lengkap dengan gelar]
(dan seterusnya...)

DOSEN:
1. [Nama Lengkap dengan gelar], ST., MT.
2. [Nama Lengkap dengan gelar], M.Eng.
(dan seterusnya...)

STATISTIK:
- Profesor: X orang
- Lektor Kepala & Doktor: Y orang
- Dosen: Z orang
- TOTAL: XYZ orang

Catatan:
Data diambil dari database akademik UI dan website resmi Departemen Teknik Elektro.
Untuk informasi lebih lanjut, kunjungi: https://ee.ui.ac.id/staff-pengajar/

PENTING: 
- JANGAN gunakan emoji, symbol, atau formatting berlebihan!
- Format SIMPLE dan CLEAN
- Gunakan numbering (1., 2., 3., ...) untuk daftar nama
- Jangan return "Tidak ada nama" jika data tersedia!

Ekstrak sekarang dengan format SIMPLE dan CLEAN:"""
        else:
            extraction_prompt = f"""Extract ALL professors and lecturers from this data.

User request: "{query}"

Available data:
{combined_context}

**CRITICAL RULES:**
1. Extract ALL faculty names found (Prof., Dr., Ir., etc.)
2. IGNORE: Navigation menus ("Program Studi", "Laboratorium", "Riset", etc.)
3. NO DUPLICATES - each name should appear ONLY ONCE
4. Group by rank:
   - Professors (Prof. Dr. / Prof. Ir. / Prof.)
   - Associate Professors / Doctorate (Dr. / Ir.)
   - Lecturers (those without Prof/Dr titles)
5. Format: Numbering (1., 2., 3., ...) for easy reading
6. MANDATORY: Extract at least 20 names! If less than 20, extract all available.

**OUTPUT FORMAT (SIMPLE & CLEAN - NO EMOJI!):**

FACULTY LIST - ELECTRICAL ENGINEERING DEPARTMENT UI

PROFESSORS:
1. Prof. Dr. Ir. [Full Name with titles]
2. Prof. Dr. [Full Name with titles]
3. Prof. Ir. [Full Name with titles]
(continue...)

ASSOCIATE PROFESSORS & DOCTORATE:
1. Dr. Eng. [Full Name with titles]
2. Dr. Ir. [Full Name with titles]
3. Dr. [Full Name with titles]
(continue...)

LECTURERS:
1. [Full Name with titles], ST., MT.
2. [Full Name with titles], M.Eng.
(continue...)

STATISTICS:
- Professors: X people
- Associate Professors & Doctorate: Y people
- Lecturers: Z people
- TOTAL: XYZ people

Note:
Data sourced from UI academic database and official Electrical Engineering Department website.
For more information, visit: https://ee.ui.ac.id/staff-pengajar/

IMPORTANT:
- DO NOT use emojis, symbols, or excessive formatting!
- Keep it SIMPLE and CLEAN
- Use numbering (1., 2., 3., ...) for name lists
- Don't return "No names found" if data is available!

Extract now with SIMPLE and CLEAN format:"""
        
        try:
            raw_output = self.llm.call([{"role": "user", "content": extraction_prompt}])
            
            print(f"  [DEBUG] LLM raw output length: {len(str(raw_output))} characters")  # DEBUG
            print(f"  [DEBUG] LLM output preview: {str(raw_output)[:500]}...")  # DEBUG
            
            # LESS AGGRESSIVE deduplication (only for exact duplicates)
            cleaned_output = self._deduplicate_names_gentle(raw_output)
            
            # Length safety check
            if len(cleaned_output) > 5000:
                print("  ⚠️ Output too long, truncating...")
                cleaned_output = cleaned_output[:5000] + "\n\n[Output truncated for safety]"
            
            print(f"  ✓ Final output: {len(cleaned_output)} characters")
            return cleaned_output
            
        except Exception as e:
            print(f"  ✗ LLM error: {e}")
            return self._emergency_fallback(query)
    
    def _deduplicate_names_gentle(self, text: str) -> str:
        """Gently remove EXACT duplicate lines only (less aggressive)."""
        lines = text.split('\n')
        seen_lines = set()
        deduplicated_lines = []
        
        for line in lines:
            clean_line = line.strip()
            
            # Keep all non-name lines (headers, separators, notes)
            if not clean_line.startswith('•') and not clean_line.startswith('-'):
                deduplicated_lines.append(line)
                continue
            
            # For name lines, only remove EXACT duplicates
            if clean_line not in seen_lines:
                seen_lines.add(clean_line)
                deduplicated_lines.append(line)
        
        return '\n'.join(deduplicated_lines)
    
    def _deduplicate_names(self, text: str) -> str:
        """Aggressively remove duplicate names (OLD METHOD - kept for compatibility)."""
        lines = text.split('\n')
        seen_names = set()
        deduplicated_lines = []
        
        for line in lines:
            # Check if line contains a name
            if line.strip().startswith('-') or any(title in line for title in ['Prof.', 'Dr.', 'Ir.']):
                # Extract core name
                core_name = re.sub(r'(Prof\.|Dr\.|Ir\.|M\.Sc|M\.Eng|M\.T|Ph\.D|ST\.)', '', line)
                core_name = re.sub(r'[,\-\.]', '', core_name).strip()
                
                # Only add if not seen before
                if core_name not in seen_names and len(core_name) > 5:
                    seen_names.add(core_name)
                    deduplicated_lines.append(line)
            else:
                # Keep non-name lines (headers, etc.)
                deduplicated_lines.append(line)
        
        return '\n'.join(deduplicated_lines)  # FIXED: Added missing quote before .join()
    
    def _crewai_complex_query(self, query: str, user_urls: list = None) -> str:
        """Use CrewAI for complex queries that need multi-step reasoning."""
        print("\n[CREWAI MODE] Initializing agent...")
        
        try:
            agent = Agent(
                role='Academic Information Specialist',
                goal='Provide accurate academic information',
                backstory=(
                    "You are a focused research assistant.\n"
                    "1. Check database first\n"
                    "2. Use SINTA/Scholar for enrichment if needed\n"
                    "3. Keep responses concise (max 500 words)\n"
                    "4. NO REPETITION - each fact should appear ONCE\n"
                ),
                tools=[
                    academic_search_tool,
                    sinta_scraper_tool,
                    google_scholar_tool,
                    dynamic_web_scraper_tool,
                ],
                llm=self.llm,
                verbose=True,
                allow_delegation=False,
                max_iter=3,
            )
            
            task = Task(
                description=f"""Answer: "{query}"

**STRICT RULES:**
1. Check database FIRST
2. Maximum 500 words output
3. NO REPETITION of information
4. If query is about specific person, use SINTA/Scholar for validation

Answer concisely:""",
                expected_output="Concise, non-repetitive answer (max 500 words)",
                agent=agent
            )
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )
            
            result = crew.kickoff()
            
            # Extract and validate
            if hasattr(result, 'raw'):
                output = str(result.raw)
            elif hasattr(result, 'output'):
                output = str(result.output)
            else:
                output = str(result)
            
            # Safety checks
            output = self._safety_check(output)
            
            return output
            
        except Exception as e:
            print(f"[ERROR] CrewAI failed: {e}")
            return self._emergency_fallback(query)
    
    def _safety_check(self, output: str) -> str:
        """Check for infinite loops and duplicates."""
        lines = output.split('\n')
        line_counts = {}
        
        for line in lines:
            clean_line = line.strip()
            if len(clean_line) > 20:
                line_counts[clean_line] = line_counts.get(clean_line, 0) + 1
        
        max_repeats = max(line_counts.values()) if line_counts else 0
        
        if max_repeats > 3:
            print(f"[SAFETY] Detected infinite loop! (max repeats: {max_repeats})")
            print("[SAFETY] Triggering emergency fallback...")
            return "[SYSTEM ERROR: Agent entered infinite loop. Using fallback...]\n\n" + self._emergency_fallback("list professors")
        
        if len(output) > 10000:
            print("[SAFETY] Output too long, truncating...")
            output = output[:10000] + "\n\n[Output truncated for safety]"
        
        return output
    
    def _emergency_fallback(self, query: str) -> str:
        """Emergency response when everything fails."""
        return f"""# Dosen Departemen Teknik Elektro UI

Mohon maaf, sistem mengalami kesulitan teknis.

**Silakan kunjungi:**
- Website Resmi: https://ee.ui.ac.id/staff-pengajar/
- SINTA UI: https://sinta.kemdikbud.go.id/affiliations/detail?id=147

**Atau coba query yang lebih spesifik:**
- "Prof. Riri Fitri Sari"
- "daftar 10 profesor di Teknik Elektro UI"

Maaf atas ketidaknyamanannya."""

# Singleton
_rag = None

def get_rag():
    global _rag
    if _rag is None:
        _rag = HybridRAG()
    return _rag

def run_agentic_rag_crew(query: str, user_urls: list[str] | None = None):
    """Main entry point - HYBRID system with intelligent routing."""
    try:
        rag = get_rag()
        return rag.query(query, user_urls)
    except Exception as e:
        print(f"[CRITICAL] System failure: {e}")
        import traceback
        traceback.print_exc()
        
        return f"""# System Error

Error: {str(e)}

**Sumber Manual:**
- https://ee.ui.ac.id/staff-pengajar/
- https://sinta.kemdikbud.go.id

Silakan coba lagi."""
