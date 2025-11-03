"""
CV Generation Agent System using CrewAI
This module uses AI agents to intelligently gather and structure CV data from multiple sources.
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from tools import (
    academic_search_tool,
    sinta_scraper_tool,
    google_scholar_tool,
    web_search_tool,
    dynamic_web_scraper_tool
)
import re

load_dotenv()

# Initialize LLM for agents
llm = LLM(
    model="gemini/gemini-2.0-flash-exp",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
    max_tokens=4000,
)

def clean_tool_output(text: str, max_chars: int = 1500) -> str:
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
        'database': None,
        'sinta': None,
        'scholar': None,
        'raw_info': {}
    }
    
    # Step 1: Collect data from tools with error handling
    print("\n[1/4] Collecting data from Academic Database...")
    try:
        db_result = academic_search_tool._run(professor_name)
        collected_data['database'] = clean_tool_output(db_result, 1000)
        collected_data['raw_info'].update(extract_key_info(db_result))
        print(f"  ✓ Database: {len(db_result)} chars → {len(collected_data['database'])} chars (cleaned)")
    except Exception as e:
        print(f"  ✗ Database error: {e}")
    
    print("\n[2/4] Collecting data from SINTA...")
    try:
        sinta_result = sinta_scraper_tool._run(professor_name)
        collected_data['sinta'] = clean_tool_output(sinta_result, 800)
        collected_data['raw_info'].update(extract_key_info(sinta_result))
        print(f"  ✓ SINTA: {len(sinta_result)} chars → {len(collected_data['sinta'])} chars (cleaned)")
    except Exception as e:
        print(f"  ✗ SINTA error: {e}")
    
    print("\n[3/4] Collecting data from Google Scholar...")
    try:
        scholar_result = google_scholar_tool._run(professor_name)
        collected_data['scholar'] = clean_tool_output(scholar_result, 1200)
        print(f"  ✓ Scholar: {len(scholar_result)} chars → {len(collected_data['scholar'])} chars (cleaned)")
    except Exception as e:
        print(f"  ✗ Scholar error: {e}")
    
    # Step 2: Create compact context for LLM
    print("\n[4/4] Generating CV with LLM...")
    
    compact_context = f"""DATA SOURCES FOR {professor_name}:

DATABASE:
{collected_data['database'] or 'Not available'}

SINTA PROFILE:
{collected_data['sinta'] or 'Not available'}

GOOGLE SCHOLAR:
{collected_data['scholar'][:500] if collected_data['scholar'] else 'Not available'}

EXTRACTED INFO:
Name: {collected_data['raw_info'].get('name', professor_name)}
Birth: {collected_data['raw_info'].get('birth', 'Not available')}
SINTA Score: {collected_data['raw_info'].get('sinta_score', 'Not available')}
Research Areas: {', '.join(collected_data['raw_info'].get('research_areas', [])) or 'Not available'}
"""

    prompt = f"""You are creating a professional academic CV. Extract ALL available information from the provided data sources.

{compact_context}

Create a comprehensive CV using this EXACT structure:

# [Full Name with ALL academic titles - Prof., Dr., Ir., etc.]

## PERSONAL INFORMATION
- Position: [Extract exact position/title from data - e.g., "Professor", "Guru Besar", "Associate Professor"]
- Affiliation: Universitas Indonesia
- Department: [Extract department if mentioned, otherwise "Departemen Teknik Elektro"]
- Born: [Extract birth date and place if available]
- Email: [Extract email if found]

## EDUCATION
[List ALL degrees found with institution and year if available. Format as bullet points:]
- [Degree] from [Institution], [Year]
- [Degree] from [Institution], [Year]

If no education data found: "- Data not available in sources"

## CURRENT POSITIONS
[List ALL current positions/roles found. Format as bullet points:]
- [Position] at [Institution/Organization]
- [Position] at [Institution/Organization]

If no positions found: "- Data not available in sources"

## RESEARCH INTERESTS
[Extract ALL research areas, topics, or keywords mentioned. Format as bullet points:]
- [Research Area 1]
- [Research Area 2]
- [Research Area 3]

Examples: Protocol Engineering, Computer Networks, IoT, ICT Implementation, etc.

If no research areas found: "- Data not available in sources"

## PUBLICATIONS
[List ALL publications found from Google Scholar or other sources. Format as bullet points with bold titles:]
- **[Paper Title]** Authors: [Authors]. [Journal/Conference], [Year]. [Citations info if available]

List up to 10 most important publications. If more than 10, list the most cited or recent ones.

If no publications found: "- Data not available in sources"

## ACADEMIC METRICS
- SINTA Score: [Extract score if found, otherwise "Not available"]
- Google Scholar Citations: [Extract total citations if found, otherwise "Not available"]
- H-Index: [Extract if found, otherwise "Not available"]

## EXTERNAL PROFILES
- SINTA: [Extract URL or use: https://sinta.kemdikbud.go.id/authors/profile/5977168]
- Google Scholar: [Extract URL if found]
- Scopus: [Extract URL if found]

## AWARDS AND RECOGNITION
[If any awards, honors, or recognition mentioned, list them here. Otherwise omit this section]

---

**CRITICAL INSTRUCTIONS:**
1. Extract EVERY piece of information from the data sources provided
2. For PUBLICATIONS section: Look carefully in the Google Scholar data and list actual paper titles
3. For RESEARCH INTERESTS: Extract keywords, topics, and research areas mentioned
4. For EDUCATION: Look for degree information (S1, S2, S3, Bachelor, Master, PhD, etc.)
5. Do NOT write "Information not available" unless you truly cannot find ANY data
6. If a section has data, include ALL of it (don't truncate)
7. Clean up any HTML tags or formatting issues
8. Use proper markdown formatting with bullet points (-)
9. For publications, prioritize extracting actual titles from Google Scholar data

Generate the complete CV now:"""

    try:
        response = llm.call([{"role": "user", "content": prompt}])
        cv_text = str(response).strip()
        
        # Validate response
        if not cv_text or len(cv_text) < 100:
            raise ValueError("LLM returned insufficient content")
        
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
