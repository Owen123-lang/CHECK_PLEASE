"""
CV Generation Agent System using CrewAI
This module uses AI agents to intelligently gather and structure CV data from multiple sources.
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from tools import (
    academic_search_tool,
    google_scholar_tool,
    web_search_tool,
    dynamic_web_scraper_tool,
    ui_scholar_search_tool,  # Add UI Scholar tool
    eng_ui_personnel_scraper_tool  # NEW: Official eng.ui.ac.id personnel scraper
)
from cv_prompts import get_cv_generation_prompt  # 🔥 NEW: Import simplified prompt
import re

load_dotenv()

# Initialize LLM for agents with MUCH higher token limit for comprehensive CVs
# Using gemini-2.5-pro (latest & best) for SUPERIOR instruction following
llm = LLM(
    model="gemini/gemini-2.5-pro",  # Latest Gemini model - best instruction following
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1,  # Slightly increased from 0.0 to allow more creativity in extraction
    max_tokens=16000,  # Need space for 15-20 publications with full details
)

def clean_tool_output(text: str, max_chars: int = 3500) -> str:
    """Clean and truncate tool output to avoid context overflow."""
    # Remove HTML-like tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # Truncate if too long
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
    return text

def extract_key_info(text: str) -> dict:
    """Extract key structured information from text."""
    info = {
        'name': '',
        'title': '',
        'birth': '',
        'affiliation': '',
        'sinta_score': '',
        'research_areas': [],
        'education': []
    }
    
    # Extract name with title
    name_match = re.search(r'(?:Prof\.\s*)?(?:Dr\.\s*)?(?:Ir\.\s*)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text)
    if name_match:
        info['name'] = name_match.group(0)
    
    # Extract birth info
    birth_match = re.search(r'(?:Lahir|Born)(?:\s*:)?\s*([^,\n]+,\s*\d{4})', text, re.IGNORECASE)
    if birth_match:
        info['birth'] = birth_match.group(1)
    
    # Extract SINTA score
    sinta_match = re.search(r'SINTA Score[:\s]+(\d+\.?\d*)', text)
    if sinta_match:
        info['sinta_score'] = sinta_match.group(1)
    
    # Extract research areas
    research_patterns = [
        r'Protocol Engineering',
        r'Computer Network',
        r'IoT',
        r'ICT implementation',
        r'University ranking'
    ]
    for pattern in research_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            info['research_areas'].append(pattern)
    
    return info

def simplified_cv_generation(professor_name: str, session_id: str = None) -> dict:
    """
    Simplified CV generation that avoids LLM context overflow.
    Direct tool usage with pre-processed outputs.
    """
    
    print("\n" + "="*80)
    print(f"🤖 SIMPLIFIED CV GENERATION FOR: {professor_name}")
    print("="*80)
    
    collected_data = {
        'eng_ui_personnel': None,  # NEW: Official eng.ui.ac.id personnel page (HIGHEST PRIORITY)
        'database': None,
        'ui_scholar': None,  # Add UI Scholar data
        'scholar': None,
        'raw_info': {}
    }
    
    # Step 0: Try to get official data from eng.ui.ac.id FIRST (highest priority)
    print("\n[0/5] 🌐 Collecting OFFICIAL data from eng.ui.ac.id personnel page...")
    try:
        eng_ui_result = eng_ui_personnel_scraper_tool._run(professor_name)
        collected_data['eng_ui_personnel'] = clean_tool_output(eng_ui_result, 3500)
        print(f"  ✓ ENG.UI.AC.ID: {len(eng_ui_result)} chars → {len(collected_data['eng_ui_personnel'])} chars (cleaned)")
        print(f"  📋 This is the AUTHORITATIVE source for education, research expertise, and latest publications")
    except Exception as e:
        print(f"  ✗ ENG.UI.AC.ID error: {e}")
        print(f"  ⚠️ Will use fallback sources (database, UI Scholar, Google Scholar)")
    
    # Step 1: Collect data from tools with error handling
    print("\n[1/5] Collecting data from Academic Database...")
    try:
        db_result = academic_search_tool._run(professor_name)
        # Keep MORE data from database - increase from 1000 to 3000 chars
        collected_data['database'] = clean_tool_output(db_result, 3000)
        collected_data['raw_info'].update(extract_key_info(db_result))
        print(f"  ✓ Database: {len(db_result)} chars → {len(collected_data['database'])} chars (cleaned)")
    except Exception as e:
        print(f"  ✗ Database error: {e}")
    
    print("\n[2/5] Collecting data from UI Scholar (scholar.ui.ac.id)...")
    try:
        ui_scholar_result = ui_scholar_search_tool._run(f"{professor_name} publications")
        # Keep UI Scholar data - 2500 chars
        collected_data['ui_scholar'] = clean_tool_output(ui_scholar_result, 2500)
        print(f"  ✓ UI Scholar: {len(ui_scholar_result)} chars → {len(collected_data['ui_scholar'])} chars (cleaned)")
    except Exception as e:
        print(f"  ✗ UI Scholar error: {e}")
    
    print("\n[3/5] Collecting data from Google Scholar...")
    try:
        scholar_result = google_scholar_tool._run(professor_name)
        # Keep MORE data from Scholar - increase from 1200 to 2500 chars
        collected_data['scholar'] = clean_tool_output(scholar_result, 2500)
        print(f"  ✓ Scholar: {len(scholar_result)} chars → {len(collected_data['scholar'])} chars (cleaned)")
    except Exception as e:
        print(f"  ✗ Scholar error: {e}")
    
    # Step 4: Create compact context for LLM
    print("\n[4/5] Generating CV with LLM...")
    
    compact_context = f"""DATA SOURCES FOR {professor_name}:

🌐 ENG.UI.AC.ID OFFICIAL PERSONNEL PAGE (from eng.ui.ac.id - AUTHORITATIVE SOURCE):
{collected_data['eng_ui_personnel'] if collected_data['eng_ui_personnel'] else 'Not available - will use fallback sources'}

DATABASE INFORMATION (from RAG vector database):
{collected_data['database'] or 'Not available'}

UI SCHOLAR PUBLICATIONS (from scholar.ui.ac.id - PRIMARY SOURCE for UI faculty):
{collected_data['ui_scholar'] if collected_data['ui_scholar'] else 'Not available'}

GOOGLE SCHOLAR PUBLICATIONS (from Google Scholar API):
{collected_data['scholar'] if collected_data['scholar'] else 'Not available'}

EXTRACTED KEY INFO:
Name: {collected_data['raw_info'].get('name', professor_name)}
Birth: {collected_data['raw_info'].get('birth', 'Not available')}
SINTA Score: {collected_data['raw_info'].get('sinta_score', 'Not available')}
Research Areas: {', '.join(collected_data['raw_info'].get('research_areas', [])) or 'Not available'}
"""

    # 🔥 USE NEW SIMPLIFIED PROMPT from cv_prompts.py
    prompt = get_cv_generation_prompt(professor_name, compact_context)

    try:
        response = llm.call([{"role": "user", "content": prompt}])
        cv_text = str(response).strip()
        
        # Validate response LENGTH (should be at least 5000 chars for 10+ publications)
        if not cv_text or len(cv_text) < 100:
            raise ValueError("LLM returned insufficient content")
        
        # 🚨 CRITICAL VALIDATION: Check publication count
        publication_count = cv_text.lower().count('\n- **') + cv_text.lower().count('\n1. **') + cv_text.lower().count('\n2. **')
        if publication_count < 8:
            print(f"  ⚠️ WARNING: Only {publication_count} publications found in output (expected 10+)")
            print(f"  ⚠️ LLM output length: {len(cv_text)} chars (should be 5000+ for complete CV)")
        
        # 🚨 CRITICAL FIX: Convert [at] notation to @ BEFORE returning to PDF generator
        cv_text = cv_text.replace('[at]', '@').replace('[ at ]', '@').replace(' [at] ', '@')
        print(f"  ✓ Email [at] notation converted to @ symbol")
        
        print(f"  ✓ CV generated: {len(cv_text)} characters")
        
        # DEBUG: Print first 500 chars to see actual format
        print("\n" + "="*80)
        print("[DEBUG] CV TEXT PREVIEW (first 500 chars):")
        print("="*80)
        print(cv_text[:500])
        print("="*80 + "\n")
        
        return {
            "success": True,
            "professor_name": professor_name,
            "cv_text": cv_text,
            "metadata": {
                "generated_by": "Simplified CV Generator",
                "character_count": len(cv_text),
                "sources_used": [k for k, v in collected_data.items() if v and k != 'raw_info']
            }
        }
        
    except Exception as e:
        print(f"  ✗ LLM error: {e}")
        
        # Fallback: Create basic CV from extracted data
        fallback_cv = f"""# {collected_data['raw_info'].get('name', professor_name)}

## PERSONAL INFORMATION
- Position: Professor
- Affiliation: Universitas Indonesia
- Born: {collected_data['raw_info'].get('birth', 'Not available')}

## RESEARCH INTERESTS
{chr(10).join(['- ' + area for area in collected_data['raw_info'].get('research_areas', ['Not available'])])}

## ACADEMIC METRICS
- SINTA Score: {collected_data['raw_info'].get('sinta_score', 'Not available')}

## EXTERNAL PROFILES
- SINTA: https://sinta.kemdiktisaintek.go.id/authors/profile/5977168

---
*Note: This CV was automatically generated with limited data. For complete information, please visit the official profiles above.*
"""
        
        return {
            "success": True,
            "professor_name": professor_name,
            "cv_text": fallback_cv,
            "metadata": {
                "generated_by": "Fallback Generator (LLM failed)",
                "character_count": len(fallback_cv),
                "warning": str(e)
            }
        }

def generate_cv_with_agents(professor_name: str, session_id: str = None) -> dict:
    """
    Main CV generation function - now uses simplified approach to avoid LLM failures.
    """
    print(f"\n[CV GENERATOR] Using simplified generation approach for: {professor_name}")
    return simplified_cv_generation(professor_name, session_id)

def quick_cv_generation(professor_name: str) -> str:
    """
    Quick CV generation without full agent workflow (fallback).
    Uses existing cv_generator_tool.
    """
    from tools import cv_generator_tool
    
    print(f"\n[QUICK CV] Generating CV for: {professor_name}")
    result = cv_generator_tool._run(professor_name)
    return result
