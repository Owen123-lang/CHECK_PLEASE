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
    dynamic_web_scraper_tool
)
import re

load_dotenv()

# Initialize LLM for agents with higher token limit for detailed CVs
llm = LLM(
    model="gemini/gemini-2.0-flash-exp",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
    max_tokens=8000,  # Increased for more detailed output
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
        'database': None,
        'sinta': None,
        'scholar': None,
        'raw_info': {}
    }
    
    # Step 1: Collect data from tools with error handling
    print("\n[1/4] Collecting data from Academic Database...")
    try:
        db_result = academic_search_tool._run(professor_name)
        # Keep MORE data from database - increase from 1000 to 3000 chars
        collected_data['database'] = clean_tool_output(db_result, 3000)
        collected_data['raw_info'].update(extract_key_info(db_result))
        print(f"  ✓ Database: {len(db_result)} chars → {len(collected_data['database'])} chars (cleaned)")
    except Exception as e:
        print(f"  ✗ Database error: {e}")
    
    print("\n[2/4] Collecting data from Google Scholar...")
    try:
        scholar_result = google_scholar_tool._run(professor_name)
        # Keep MORE data from Scholar - increase from 1200 to 2500 chars
        collected_data['scholar'] = clean_tool_output(scholar_result, 2500)
        print(f"  ✓ Scholar: {len(scholar_result)} chars → {len(collected_data['scholar'])} chars (cleaned)")
    except Exception as e:
        print(f"  ✗ Scholar error: {e}")
    
    # Step 2: Create compact context for LLM
    print("\n[3/4] Generating CV with LLM...")
    
    compact_context = f"""DATA SOURCES FOR {professor_name}:

DATABASE INFORMATION:
{collected_data['database'] or 'Not available'}

GOOGLE SCHOLAR PUBLICATIONS:
{collected_data['scholar'] if collected_data['scholar'] else 'Not available'}

EXTRACTED KEY INFO:
Name: {collected_data['raw_info'].get('name', professor_name)}
Birth: {collected_data['raw_info'].get('birth', 'Not available')}
SINTA Score: {collected_data['raw_info'].get('sinta_score', 'Not available')}
Research Areas: {', '.join(collected_data['raw_info'].get('research_areas', [])) or 'Not available'}
"""

    prompt = f"""You are an expert academic CV writer. Create a COMPREHENSIVE and DETAILED professional CV from the provided data sources.

{compact_context}

**YOUR MISSION**: Extract and present EVERY piece of information available. This CV should be thorough and professional.

Create a detailed CV using this EXACT structure:

# [Full Name with ALL academic titles - Prof., Dr., Ir., M.T., Ph.D., etc.]

## PERSONAL INFORMATION
- **Position**: [Extract exact position/title - e.g., "Professor", "Lecturer", "Senior Lecturer", "Guru Besar"]
- **Affiliation**: [Extract university name - usually Universitas Indonesia]
- **Department**: [Extract full department name if mentioned, e.g., "Departemen Teknik Elektro"]
- **Born**: [Extract birth date and place if available, e.g., "Jakarta, 15 Maret 1980"]
- **Email**: [Extract email address if found. Format as: name[at]ui.ac.id or full email]
- **Phone**: [Extract phone number if found]
- **Office**: [Extract office location/room if mentioned]
- **SINTA ID**: [Extract SINTA ID if found]
- **Scholar ID**: [Extract Google Scholar ID if found]

## ACADEMIC BACKGROUND

### Education History
[List ALL degrees chronologically, newest first. Include as much detail as possible:]
- **[Degree Title]** (e.g., Ph.D., S3, Doctoral) in [Field], [University Name], [Country], [Year]
  - Dissertation: [Title if mentioned]
  - Advisor: [Name if mentioned]
- **[Degree Title]** (e.g., M.T., S2, Master) in [Field], [University Name], [Country], [Year]
  - Thesis: [Title if mentioned]
- **[Degree Title]** (e.g., S.T., S1, Bachelor) in [Field], [University Name], [Country], [Year]

If no education data found: "- Education history not available in sources"

### Academic Titles & Certifications
[If any academic titles (Lektor, Lektor Kepala, etc.) or certifications are mentioned, list them here]

## CURRENT POSITIONS & ROLES
[List ALL current positions, roles, and responsibilities:]
- **[Position Title]** at [Institution/Organization]
  - [Additional details about the role if available]
- **[Position Title]** at [Institution/Organization]

Examples: Lecturer, Head of Laboratory, Program Coordinator, Committee Member, etc.

If no positions found: "- Current positions not available in sources"

## RESEARCH INTERESTS & EXPERTISE
[Extract and group ALL research areas, expertise, and keywords. Be specific and comprehensive:]

### Primary Research Areas:
- [Main Research Area 1] - [Brief description if available]
- [Main Research Area 2] - [Brief description if available]

### Specialized Topics:
- [Specific Topic 1]
- [Specific Topic 2]
- [Specific Topic 3]

### Keywords:
[List all relevant keywords: e.g., Energy Systems, Control Optimization, Power Electronics, Smart Grid, Renewable Energy, Machine Learning, etc.]

If no research areas found: "- Research interests not available in sources"

## PUBLICATIONS & SCHOLARLY WORKS

**CRITICAL VALIDATION RULE FOR PUBLICATIONS:**
- **Extract publications from BOTH the DATABASE INFORMATION section AND the GOOGLE SCHOLAR PUBLICATIONS section**
- **ONLY include publications where the person's name ({professor_name}) appears in the author list**
- **CHECK CAREFULLY**: Each publication must be authored or co-authored by {professor_name}
- **DO NOT include publications from other people with similar names**
- **DO NOT include publications that are just mentioned as references or citations**
- **If the author list doesn't explicitly contain {professor_name} or their surname, SKIP that publication**

### Journal Articles
[List ONLY journal publications where {professor_name} is an author. Extract from BOTH database and scholar data. Format each as:]
- **[Complete Paper Title]**
  - Authors: [{professor_name}'s name or surname must be in this list]
  - Journal: [Journal name]
  - Year: [Publication year]
  - DOI/Link: [If available]
  - Citations: [Number if available]

### Conference Papers
[List ONLY conference papers where {professor_name} is an author. Extract from BOTH database and scholar data:]
- **[Complete Paper Title]**
  - Authors: [{professor_name}'s name or surname must be in this list]
  - Conference: [Full conference name]
  - Location: [City, Country if available]
  - Year: [Year]
  - Citations: [Number if available]

### Books & Book Chapters
[If any books or book chapters are mentioned where {professor_name} is an author, list them here]

**EXTRACTION INSTRUCTIONS**:
1. **First**, look through the DATABASE INFORMATION section for publication titles, paper names, or research output
2. **Second**, look through the GOOGLE SCHOLAR PUBLICATIONS section
3. For EACH publication found, verify that {professor_name}'s surname appears in the author list
4. Only extract publications that are CLEARLY authored or co-authored by {professor_name}
5. If you see a publication title but NO author list, try to verify it belongs to {professor_name} from context
6. If unsure whether a publication belongs to this person, SKIP it
7. List at least 10-15 VERIFIED publications if available from both sources combined
8. Better to have fewer accurate publications than many irrelevant ones

If no publications found: "- Publications not available in sources"

## RESEARCH PROJECTS & GRANTS
[If any research projects, grants, or funding information is mentioned, list them here with details]

## TEACHING & COURSES
[If any teaching activities or courses taught are mentioned, list them here]

## ACADEMIC METRICS & IMPACT

### Citation Metrics
- **Total Citations**: [Extract from Google Scholar data]
- **H-Index**: [Extract if available]
- **i10-Index**: [Extract if available]
- **SINTA Score**: [Extract if found]
- **Scopus H-Index**: [Extract if available]

### Research Output
- **Total Publications**: [Count if available]
- **Journal Articles**: [Count if available]
- **Conference Papers**: [Count if available]

If metrics not available: "- Metrics data not available in sources"

## PROFESSIONAL MEMBERSHIPS & AFFILIATIONS
[If any professional society memberships or affiliations are mentioned, list them]

## AWARDS, HONORS & RECOGNITION
[List ALL awards, honors, grants, recognitions, or achievements mentioned]

## EXTERNAL PROFILES & LINKS
- **SINTA**: [Extract full URL if found, otherwise use: https://sinta.kemdikbud.go.id/authors/profile/]
- **Google Scholar**: [Extract full URL if found]
- **Scopus**: [Extract Author ID or URL if found]
- **ORCID**: [Extract if found]
- **ResearchGate**: [Extract if found]
- **LinkedIn**: [Extract if found]
- **University Profile**: [Extract if found]

## CONTACT & ADDITIONAL INFORMATION
[Any other relevant information not covered above]

---

**CRITICAL QUALITY STANDARDS:**

1. **COMPLETENESS**: Extract EVERY piece of information from the data sources. Don't leave anything out.

2. **PUBLICATIONS**: This is crucial! Look carefully through the Google Scholar data and extract:
   - Complete paper titles (not truncated)
   - All author names
   - Journal/conference names
   - Publication years
   - Citation counts
   - List at least 10-15 publications if available

3. **DETAIL**: For each section, extract all available details. If a piece of information exists in the source data, include it in the CV.

4. **RESEARCH INTERESTS**: Extract ALL keywords, topics, and research areas mentioned anywhere in the data. Be thorough.

5. **EDUCATION**: Look for all degree information including:
   - Degree types (S1, S2, S3, Bachelor, Master, PhD, etc.)
   - Universities (both Indonesian and international)
   - Years of graduation
   - Thesis/dissertation titles if mentioned

6. **NO PLACEHOLDERS**: Only write "Not available" if you truly cannot find ANY data for that specific field after thoroughly searching all sources.

7. **FORMATTING**: Use proper markdown with:
   - Bold (**text**) for emphasis
   - Bullet points (-) for lists
   - Proper headers (##, ###)
   - Clean, professional layout

8. **DATA EXTRACTION PRIORITY**:
   - Look for actual content in DATABASE INFORMATION section first
   - Then check GOOGLE SCHOLAR PUBLICATIONS section
   - Extract publication titles, authors, years, citations
   - Don't summarize - include full details

Now generate the COMPLETE, DETAILED, COMPREHENSIVE CV:"""

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
