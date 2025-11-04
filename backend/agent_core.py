import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from tools import academic_search_tool, dynamic_web_scraper_tool, google_scholar_tool, sinta_scraper_tool, cv_generator_tool
import re
from collections import OrderedDict

load_dotenv()

class HybridRAG:
    """
    HYBRID RAG System:
    - Simple queries (lists) → DIRECT execution (NO CrewAI!)
    - Complex queries → CrewAI with strict limits
    - CV Generation → Special handling with CV tool
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
    
    def query(self, user_query: str, user_urls: list = None, conversation_history: list = None) -> str:
        """
        Process a user query using the Hybrid RAG system.
        
        Args:
            user_query: The user's question
            user_urls: Optional URLs to scrape for additional context
            conversation_history: Previous conversation for context
        
        Returns:
            AI-generated response
        """
        try:
            print("\n" + "=" * 70)
            print("🚀 HYBRID RAG QUERY PROCESSING")
            print("=" * 70)
            print(f"📝 Query: {user_query}")
            
            # NEW: Resolve pronouns using conversation history
            if conversation_history:
                resolved_query = self._resolve_pronouns_in_query(user_query, conversation_history)
                print(f"🔍 Resolved Query: {resolved_query}")
                # Use resolved query for processing
                processing_query = resolved_query
            else:
                processing_query = user_query
            
            # Format conversation context for the agent
            conversation_context = self._format_conversation_history(conversation_history) if conversation_history else ""
            
            # STEP 1: Vector Search (Astra DB)
            print("\n[STEP 1/4] 🔎 Vector Search (Astra DB)...")
            vector_results = self._vector_search(processing_query)
            
            # STEP 2: Conditional Web Scraping
            print("\n[STEP 2/4] 🌐 Web Scraping...")
            scraped_data = ""
            if user_urls:
                scraped_data = self._scrape_urls(user_urls)
            
            # STEP 3: Construct Context for Agents
            print("\n[STEP 3/4] 📦 Building Context...")
            context = self._build_context(
                vector_results=vector_results,
                scraped_data=scraped_data,
                conversation_context=conversation_context
            )
            
            # STEP 4: Run CrewAI Agents
            print("\n[STEP 4/4] 🤖 Running AI Agents...")
            final_output = self._run_crew(
                query=processing_query,  # Use resolved query
                original_query=user_query,  # Keep original for reference
                context=context,
                conversation_history=conversation_history
            )
            
            # Post-processing
            print("\n[POST-PROCESSING] 🧹 Cleaning output...")
            final_output = self._filter_personal_info(final_output)
            final_output = self._safety_check(final_output)
            
            print("\n" + "=" * 70)
            print("✅ QUERY PROCESSING COMPLETE")
            print("=" * 70)
            
            return final_output
            
        except Exception as e:
            print(f"\n❌ ERROR in query processing: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._emergency_fallback(user_query)
    
    def _format_conversation_history(self, history: list) -> str:
        """Format conversation history into a readable context string."""
        if not history or len(history) == 0:
            return ""
        
        context_parts = ["PREVIOUS CONVERSATION:"]
        for msg in history[-6:]:  # Only use last 6 messages (3 exchanges) to avoid context overflow
            # Handle both formats: {"role": "user", "content": "..."} OR {"user": "...", "assistant": "..."}
            if "user" in msg and "assistant" in msg:
                # Format from main.py storage
                context_parts.append(f"User: {msg['user']}")
                context_parts.append(f"Assistant: {msg['assistant'][:500]}")  # Truncate long responses
            elif "role" in msg and "content" in msg:
                # Standard format
                role = "User" if msg["role"] == "user" else "Assistant"
                content = msg["content"]
                context_parts.append(f"{role}: {content}")
        
        context_parts.append("\n**IMPORTANT:** When the user says 'his/her/their', they are referring to the person mentioned in the previous conversation above.")
        return '\n'.join(context_parts)
    
    def _resolve_pronouns_in_query(self, query: str, conversation_history: list = None) -> str:
        """
        ✨ NEW FEATURE: Automatically resolve pronouns (his/her/their/him) to actual names from conversation history.
        This makes the chatbot behave like ChatGPT/Gemini!
        
        Example:
        User: "who is alfan prasekal"
        Bot: "Alfan Prasekal is an inventor..."
        User: "can you find more about him"  ← This function will convert to "can you find more about Alfan Prasekal"
        """
        if not conversation_history or len(conversation_history) == 0:
            return query
        
        query_lower = query.lower()
        
        # Detect if query uses pronouns
        pronouns = ['his', 'her', 'their', 'him', 'them', 'he', 'she', 'they',
                   'nya', 'dia', 'beliau', 'tersebut']  # English + Indonesian
        
        has_pronoun = any(pronoun in query_lower.split() for pronoun in pronouns)
        
        if not has_pronoun:
            return query  # No pronoun, return as-is
        
        # Extract names from recent conversation history
        extracted_names = []
        
        for msg in reversed(conversation_history[-4:]):  # Check last 4 messages (2 exchanges)
            # Get user query and assistant response
            user_msg = msg.get('user', '') if 'user' in msg else msg.get('content', '')
            assistant_msg = msg.get('assistant', '') if 'assistant' in msg else ''
            
            # Look for names in BOTH user query and assistant response
            combined_text = f"{user_msg} {assistant_msg}"
            
            # Pattern 1: "who is [Name]" or "siapa itu [Name]"
            patterns = [
                r'who is ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
                r'siapa itu ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
                r'about ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
                r'tentang ([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
                # Pattern 2: Names with titles
                r'((?:Prof\.?|Dr\.?|Ir\.?)\s+[A-Z][a-z]+(?: [A-Z][a-z]+)+)',
                # Pattern 3: Simple capitalized names (2-4 words)
                r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+)?)\b',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, combined_text)
                for match in matches:
                    name = match.strip()
                    # Validate it's a real name (not common words)
                    if len(name) > 3 and name not in ['About', 'More About', 'Information']:
                        extracted_names.append(name)
        
        if not extracted_names:
            print("[CONTEXT] No names found in history, keeping query as-is")
            return query
        
        # Use the most recent name found
        target_name = extracted_names[0]
        
        print(f"[CONTEXT] Detected pronoun reference to: '{target_name}'")
        
        # Replace pronouns with the actual name
        # Strategy: Intelligently inject the name into the query
        
        if any(phrase in query_lower for phrase in ['about him', 'about her', 'about them']):
            resolved_query = re.sub(r'about (him|her|them)', f'about {target_name}', query, flags=re.IGNORECASE)
        elif any(phrase in query_lower for phrase in ['find more about', 'more about', 'tell me about']):
            # Already has "about" - just replace pronoun
            resolved_query = query
            for pronoun in ['him', 'her', 'them', 'his', 'their']:
                resolved_query = re.sub(r'\b' + pronoun + r'\b', target_name, resolved_query, flags=re.IGNORECASE)
        elif 'his research' in query_lower or 'her research' in query_lower:
            resolved_query = re.sub(r'(his|her) research', f'{target_name}\'s research', query, flags=re.IGNORECASE)
        elif 'his publication' in query_lower or 'her publication' in query_lower:
            resolved_query = re.sub(r'(his|her) publication', f'{target_name}\'s publications', query, flags=re.IGNORECASE)
        else:
            # Generic replacement: Add name to the query
            resolved_query = f"{query} (referring to {target_name})"
        
        return resolved_query
    
    def _is_cv_request(self, query: str) -> bool:
        """Detect if user is requesting CV generation."""
        query_lower = query.lower()
        cv_keywords = [
            'generate cv', 'create cv', 'make cv', 'download cv',
            'buat cv', 'buatkan cv', 'generate curriculum vitae',
            'create curriculum vitae', 'cv untuk', 'cv for'
        ]
        return any(kw in query_lower for kw in cv_keywords)
    
    def _handle_cv_request(self, query: str) -> str:
        """Handle CV generation request by extracting professor name."""
        # Extract professor name from query
        query_lower = query.lower()
        
        name = None
        if ' for ' in query_lower:
            name = query.split(' for ', 1)[1].strip()
        elif ' untuk ' in query_lower:
            name = query.split(' untuk ', 1)[1].strip()
        else:
            # Try to find name pattern (Prof., Dr., etc.)
            name_pattern = r'((?:Prof\.?\s*)?(?:Dr\.?\s*)?(?:Ir\.?\s*)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
            match = re.search(name_pattern, query)
            if match:
                name = match.group(1)
        
        if not name:
            return """❌ Could not identify professor name for CV generation.

Please specify the professor name clearly, for example:
- "Generate CV for Prof. Dr. Riri Fitri Sari"
- "Create CV untuk Prof. Muhammad Suryanegara"
- "Buatkan CV Prof. Dadang Gunawan"

Then I'll gather all available information and prepare the CV for download."""
        
        # Use CV Generator Tool
        print(f"[CV_HANDLER] Generating CV for: {name}")
        try:
            result = cv_generator_tool._run(name)
            return result
        except Exception as e:
            print(f"[CV_HANDLER ERROR] {e}")
            return f"❌ Error generating CV: {str(e)}"
    
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
        
        return '\n'.join(deduplicated_lines)
    
    def _crewai_complex_query(self, query: str, user_urls: list = None, history_context: str = "") -> str:
        """Use CrewAI for complex queries that need multi-step reasoning."""
        print("\n[CREWAI MODE] Initializing agent...")
        
        try:
            agent = Agent(
                role='Academic Information Specialist',
                goal='Provide accurate PROFESSIONAL and ACADEMIC information ONLY',
                backstory=(
                    "You are a focused research assistant specializing in ACADEMIC and PROFESSIONAL information.\n"
                    "1. Check database first\n"
                    "2. Use SINTA/Scholar for enrichment if needed\n"
                    "3. Keep responses concise (max 500 words)\n"
                    "4. NO REPETITION - each fact should appear ONCE\n"
                    "5. NEVER include personal information (family, birth date, spouse, children, personal life)\n"
                    "6. ONLY include: academic credentials, professional positions, research, publications, awards\n"
                    "7. IMPORTANT: Pay attention to conversation history to understand pronouns like 'his/her/their'\n"
                ),
                tools=[
                    academic_search_tool,
                    sinta_scraper_tool,
                    google_scholar_tool,
                    dynamic_web_scraper_tool,
                    cv_generator_tool,
                ],
                llm=self.llm,
                verbose=True,
                allow_delegation=False,
                max_iter=3,
            )
            
            # Add conversation history to task description if available
            context_prefix = f"{history_context}\n\n" if history_context else ""
            
            task = Task(
                description=f"""{context_prefix}Answer: "{query}"

**STRICT RULES:**
1. Check database FIRST
2. Maximum 500 words output
3. NO REPETITION of information
4. If query is about specific person, use SINTA/Scholar for validation
5. **IMPORTANT: If conversation history is provided above, use it to understand who the user is asking about**
   - When user says "his/her/their", refer to the person mentioned in previous messages
   - Maintain context from previous conversation
6. **CRITICAL: ONLY include ACADEMIC and PROFESSIONAL information:**
   - ✅ Academic degrees (S1, S2, S3, PhD, etc.)
   - ✅ Professional positions (Professor, Lecturer, Chairperson, etc.)
   - ✅ Research areas and interests
   - ✅ Publications and citations
   - ✅ Academic awards and recognitions
   - ✅ SINTA score, Scopus profile, Google Scholar
   - ✅ Professional affiliations
   
   - ❌ NEVER include: Birth date, family members, spouse, children, personal life, hobbies
   - ❌ NEVER include: "Born on", "married to", "has X children", "personal information"

If the data contains personal information, SKIP IT COMPLETELY.

Answer concisely with ONLY academic and professional information:""",
                expected_output="Concise academic/professional profile (max 500 words) - NO personal information",
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
            
            # Safety checks + personal info filter
            output = self._safety_check(output)
            output = self._filter_personal_info(output)
            
            return output
            
        except Exception as e:
            print(f"[ERROR] CrewAI failed: {e}")
            return self._emergency_fallback(query)
    
    def _filter_personal_info(self, text: str) -> str:
        """Remove any personal information that slipped through."""
        print("[FILTER] Checking for personal information...")
        
        # STRICT keywords that DEFINITELY indicate personal info (not academic)
        # IMPORTANT: These must appear WITH context, not standalone
        personal_keywords = [
            ('born on', 'tanggal lahir'),  # Birth date with specific date
            ('married to', 'menikah dengan'),  # Marriage info
            ('has children', 'memiliki anak'),  # Children info
            ('family member', 'anggota keluarga'),  # Family references
            ('personal life', 'kehidupan pribadi'),  # Personal life
            ('spouse', 'pasangan'),  # Spouse info
            ('wife', 'istri'),  # Wife
            ('husband', 'suami'),  # Husband
            ('daughter', 'putri'),  # Daughter
            ('son', 'putra'),  # Son
        ]
        
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if line contains personal info keywords
            is_personal = any(
                any(kw in line_lower for kw in keyword_pair)
                for keyword_pair in personal_keywords
            )
            
            if not is_personal:
                filtered_lines.append(line)
            else:
                print(f"  [REMOVED] Personal info: {line[:80]}...")
        
        result = '\n'.join(filtered_lines)
        print(f"  ✓ Personal info filter complete")
        return result
    
    def _safety_check(self, output: str) -> str:
        """Final safety checks and formatting."""
        if len(output) > 8000:
            print("  ⚠️ Output too long, truncating...")
            output = output[:8000] + "\n\n[Output truncated for safety]"
        
        # Remove excessive repetition (same sentence appearing 3+ times)
        lines = output.split('\n')
        seen_count = {}
        deduplicated = []
        
        for line in lines:
            clean = line.strip()
            if clean:
                seen_count[clean] = seen_count.get(clean, 0) + 1
                if seen_count[clean] <= 2:  # Allow up to 2 occurrences
                    deduplicated.append(line)
        
        return '\n'.join(deduplicated)
    
    def _emergency_fallback(self, query: str) -> str:
        """Emergency fallback if everything fails."""
        return f"""⚠️ I encountered an error while processing your request.

**Your query:** "{query}"

**Possible solutions:**
1. Try rephrasing your question more specifically
2. Ask about a specific person or topic
3. Check if the information exists in our database

**What I can help with:**
- Academic profiles of UI Electrical Engineering faculty
- Research information from SINTA/Google Scholar
- Generate CV for specific professors
- List faculty members

Please try again with a more specific question!"""

    def _vector_search(self, query: str) -> str:
        """Search the Astra DB vector database for relevant academic information."""
        try:
            from tools import academic_search_tool
            result = academic_search_tool._run(query)
            print(f"  ✓ Vector search returned {len(result)} characters")
            return result
        except Exception as e:
            print(f"  ✗ Vector search failed: {e}")
            return ""
    
    def _scrape_urls(self, urls: list) -> str:
        """Scrape content from provided URLs."""
        try:
            from tools import dynamic_web_scraper_tool
            scraped_content = []
            for url in urls:
                try:
                    content = dynamic_web_scraper_tool._run(url)
                    scraped_content.append(f"From {url}:\n{content}\n")
                    print(f"  ✓ Scraped {url}")
                except Exception as e:
                    print(f"  ✗ Failed to scrape {url}: {e}")
            
            result = "\n".join(scraped_content)
            print(f"  ✓ Scraped {len(urls)} URLs, {len(result)} characters total")
            return result
        except Exception as e:
            print(f"  ✗ URL scraping failed: {e}")
            return ""
    
    def _build_context(self, vector_results: str, scraped_data: str, conversation_context: str) -> str:
        """Build context from all available sources."""
        context_parts = []
        
        if conversation_context:
            context_parts.append(f"=== CONVERSATION CONTEXT ===\n{conversation_context}\n")
        
        if vector_results:
            context_parts.append(f"=== DATABASE RESULTS ===\n{vector_results}\n")
        
        if scraped_data:
            context_parts.append(f"=== SCRAPED WEB DATA ===\n{scraped_data}\n")
        
        context = "\n".join(context_parts)
        print(f"  ✓ Built context: {len(context)} characters")
        return context
    
    def _run_crew(self, query: str, original_query: str, context: str, conversation_history: list = None) -> str:
        """Run the CrewAI agents to process the query."""
        try:
            # Format conversation context if available
            history_context = self._format_conversation_history(conversation_history) if conversation_history else ""
            
            # Create the agent
            agent = Agent(
                role='Academic Information Specialist',
                goal='Provide accurate PROFESSIONAL and ACADEMIC information ONLY',
                backstory=(
                    "You are a focused research assistant specializing in ACADEMIC and PROFESSIONAL information.\n"
                    "1. Check database first\n"
                    "2. Use SINTA/Scholar for enrichment if needed\n"
                    "3. Keep responses concise (max 500 words)\n"
                    "4. NO REPETITION - each fact should appear ONCE\n"
                    "5. NEVER include personal information (family, birth date, spouse, children, personal life)\n"
                    "6. ONLY include: academic credentials, professional positions, research, publications, awards\n"
                    "7. IMPORTANT: Pay attention to conversation history to understand pronouns like 'his/her/their'\n"
                ),
                tools=[
                    academic_search_tool,
                    sinta_scraper_tool,
                    google_scholar_tool,
                    dynamic_web_scraper_tool,
                    cv_generator_tool,
                ],
                llm=self.llm,
                verbose=True,
                allow_delegation=False,
                max_iter=3,
            )
            
            # Build task description with context
            context_prefix = ""
            if history_context:
                context_prefix += f"{history_context}\n\n"
            if context:
                context_prefix += f"AVAILABLE CONTEXT:\n{context}\n\n"
            
            task = Task(
                description=f"""{context_prefix}Answer: "{query}"

**STRICT RULES:**
1. Use the provided context from database/web searches
2. Maximum 500 words output
3. NO REPETITION of information
4. If query is about specific person, use SINTA/Scholar for validation
5. **IMPORTANT: If conversation history is provided above, use it to understand who the user is asking about**
   - When user says "his/her/their", refer to the person mentioned in previous messages
   - Maintain context from previous conversation
6. **CRITICAL: ONLY include ACADEMIC and PROFESSIONAL information:**
   - ✅ Academic degrees (S1, S2, S3, PhD, etc.)
   - ✅ Professional positions (Professor, Lecturer, Chairperson, etc.)
   - ✅ Research areas and interests
   - ✅ Publications and citations
   - ✅ Academic awards and recognitions
   - ✅ SINTA score, Scopus profile, Google Scholar
   - ✅ Professional affiliations
   
   - ❌ NEVER include: Birth date, family members, spouse, children, personal life, hobbies
   - ❌ NEVER include: "Born on", "married to", "has X children", "personal information"

If the data contains personal information, SKIP IT COMPLETELY.

Answer concisely with ONLY academic and professional information:""",
                expected_output="Concise academic/professional profile (max 500 words) - NO personal information",
                agent=agent
            )
            
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )
            
            result = crew.kickoff()
            
            # Extract result
            if hasattr(result, 'raw'):
                output = str(result.raw)
            elif hasattr(result, 'output'):
                output = str(result.output)
            else:
                output = str(result)
            
            print(f"  ✓ CrewAI completed, output: {len(output)} characters")
            return output
            
        except Exception as e:
            print(f"  ✗ CrewAI execution failed: {e}")
            import traceback
            traceback.print_exc()
            return self._emergency_fallback(query)

# Singleton
_rag = None

def get_rag():
    global _rag
    if _rag is None:
        _rag = HybridRAG()
    return _rag

def run_agentic_rag_crew(user_query: str, user_urls: list = None, conversation_history: list = None) -> str:
    """
    Main entry point for the Hybrid RAG system.
    
    Args:
        user_query: The user's question
        user_urls: Optional list of URLs to scrape
        conversation_history: Previous conversation messages for context
    
    Returns:
        AI-generated response
    """
    hybrid_rag = HybridRAG()
    return hybrid_rag.query(user_query, user_urls, conversation_history)
