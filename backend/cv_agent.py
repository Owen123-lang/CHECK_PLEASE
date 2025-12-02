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
import re

load_dotenv()

# Initialize LLM for agents with MUCH higher token limit for comprehensive CVs
llm = LLM(
    model="gemini/gemini-2.0-flash-exp",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.0,  # ZERO temperature = 100% deterministic, ABSOLUTE ZERO hallucination
    max_tokens=16000,  # DOUBLED - need space for 15-20 publications
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

    prompt = f"""You are an expert academic CV writer with STRICT ANTI-HALLUCINATION protocols.

{compact_context}

**CRITICAL RULES - VIOLATION WILL FAIL THE TASK:**

0. **DATA SOURCE PRIORITY (NEW RULE)**:
   - 🥇 **ENG.UI.AC.ID PERSONNEL PAGE**: If available, this is the AUTHORITATIVE source
   - Use eng.ui.ac.id data for: Education, Research Expertise, Latest Publications, Position
   - If eng.ui.ac.id shows education, USE IT EXACTLY (don't use other sources)
   - If eng.ui.ac.id unavailable → fallback to DATABASE + UI SCHOLAR + GOOGLE SCHOLAR
   - Example: If eng.ui.ac.id says "Bachelor, UI, 2008" → write exactly that

1. **ZERO HALLUCINATION POLICY**:
   - ONLY write information that EXISTS in the data sources above
   - DO NOT invent, guess, or create ANY information
   - If education shows "University of Leeds", DO NOT write "University of Wollongong"
   - If source says "M.Sc., Univ. of Leeds, 1997", COPY IT EXACTLY
   - When uncertain, write "Not available in sources"

2. **EDUCATION VERIFICATION**:
   - 🚨 NEW: Look for education in ENG.UI.AC.ID section FIRST (if available)
   - If eng.ui.ac.id has education data → USE IT, ignore other sources
   - If eng.ui.ac.id unavailable → Look in DATABASE INFORMATION section
   - Check for degree patterns: "Ph.D.", "M.Sc.", "S.T.", "Ir.", "Bachelor", "Master", "Doctoral"
   - Check for university names: "University of", "Universitas", "Institut"
   - COPY education entries EXACTLY as written in source data
   - DO NOT guess years, universities, or degrees
   - Example: If data says "M.Sc., University of Leeds, UK, 1997" → write EXACTLY that

3. **PUBLICATIONS EXTRACTION**:
   - YOUR PRIMARY GOAL: Extract 15-20 publications if available
   - Scan EVERY line in UI SCHOLAR, DATABASE, and GOOGLE SCHOLAR sections
   - Look for publication patterns: titles ending with periods, years in parentheses, author lists
   - Each publication MUST have: title + authors + year
   - Prioritize UI Scholar publications (most reliable for UI faculty)

**YOUR MISSION**: Extract EVERY piece of verified information. Quality = accuracy, not creativity.

Create a detailed CV using this EXACT structure:

# [Full Name with ALL academic titles - Prof., Dr., Ir., M.T., Ph.D., etc.]

## PERSONAL INFORMATION
- **Position**: [Extract exact position/title - e.g., "Professor", "Lecturer", "Senior Lecturer", "Guru Besar"]
- **Affiliation**: [Extract university name - usually Universitas Indonesia]
- **Department**: [Extract full department name if mentioned, e.g., "Departemen Teknik Elektro"]
- **Born**: [Extract birth date and place if available, e.g., "Jakarta, 15 Maret 1980"]
- **Google Scholar**: [Extract Google Scholar profile URL if found - PRIORITY FIELD. Format: https://scholar.google.com/citations?user=XXXXX]
- **UI Scholar**: [Extract UI Scholar profile URL if found. Format: https://scholar.ui.ac.id/en/persons/XXXXX]
- **Email**: [Extract email address ONLY if no Scholar links found. Use @ symbol, NOT [at]. Format: name@ui.ac.id]
- **Phone**: [Extract phone number if found]
- **Office**: [Extract office location/room if mentioned]
- **SINTA ID**: [Extract SINTA ID if found]

## ACADEMIC BACKGROUND

### Education History

**🚨 CRITICAL ANTI-HALLUCINATION PROTOCOL FOR EDUCATION 🚨**

**STEP 1: SEARCH DATA SOURCES** (NEW: Priority order)
Priority 1: Scan ENG.UI.AC.ID OFFICIAL PERSONNEL PAGE section FIRST
Priority 2: If eng.ui.ac.id unavailable, scan DATABASE INFORMATION section line by line for these EXACT patterns:
- Lines containing: "Ph.D.", "PhD", "Doctoral"
- Lines containing: "M.Sc.", "M.T.", "Master", "Magister"
- Lines containing: "S.T.", "Ir.", "Bachelor", "Sarjana"
- Lines containing: "University", "Universitas", "Institut"

**STEP 2: EXTRACT WITH REGEX VALIDATION**
For EACH line found:
✅ MUST contain: Degree name + Institution name
✅ MUST have year (19XX or 20XX)
❌ REJECT if: Same degree appears twice with different universities
❌ REJECT if: University name contradicts other entries

**STEP 3: DEDUPLICATE**
- If "S.T., Universitas Indonesia, 1997" exists
- And "Ir., Universitas Indonesia, 1993" exists
- DO NOT also list "S.T., Universitas Indonesia, 1997" again (it's duplicate!)

**STEP 4: COPY EXACTLY (NO SUBSTITUTION)**
If source says: "M.Sc., University of Leeds, UK, 1997"
→ Write EXACTLY: "- **M.Sc.**, University of Leeds, UK, 1997"

If source says: "PhD., Leeds Univ., UK, 2004"
→ Write EXACTLY: "- **Ph.D.**, Leeds Univ., UK, 2004"

**NEVER EVER**:
❌ Change "Leeds" to "Wollongong"
❌ Change "Sheffield" to "Manchester"
❌ Invent universities not in source
❌ List duplicate degrees

**FORMAT:**
- **[Exact Degree]**, [Exact University], [Country], [Year]

**If NO education found**: "- Education history not available in sources"

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

**🚨 CRITICAL MISSION: EXTRACT 15-20 PUBLICATIONS 🚨**

**WHY PUBLICATIONS ARE FEW (DIAGNOSIS):**
- Problem: LLM is being too cautious and rejecting valid publications
- Solution: Be more aggressive in extraction while maintaining quality

**NEW EXTRACTION PROTOCOL:**

### STEP 1: RAPID SCAN (Find ALL potential publications)
Scan ALL FOUR data sources line by line IN THIS PRIORITY ORDER:
1. 🌐 ENG.UI.AC.ID OFFICIAL PERSONNEL PAGE (if available - use "Latest Publications" section)
2. UI Scholar publications
3. Database information
4. Google Scholar publications

Look for these patterns:
- Lines with quotation marks containing research titles
- Lines starting with numbers (1., 2., 3.) often indicate publications
- Lines containing years (2019, 2020, 2021, etc.) near research terms
- Lines with "Journal:", "Conference:", "Published in:", "Proceedings"
- Author lists (often after "by", "Authors:", or "👥")

### STEP 2: VALIDATION (Apply these rules)
For EACH potential publication found:

✅ **ACCEPT IF:**
- Has a specific paper title (> 30 characters)
- Mentions {professor_name}'s surname OR first initial in context
- Has a year (2000-2024)
- Has venue (journal/conference name)

❌ **REJECT ONLY IF:**
- Just conference name without paper title (e.g., "IEEE Conference 2020" alone)
- Obviously unrelated author (completely different research field + different name)
- Duplicate of already listed publication

### STEP 3: PRIORITIZE BY SOURCE (UPDATED WITH ENG.UI.AC.ID)
1. **🌐 ENG.UI.AC.ID** publications (if available) → Extract ALL from "Latest Publications" section (AUTHORITATIVE)
2. **UI SCHOLAR** publications → Extract ALL (most reliable)
3. **DATABASE** publications → Extract if has title + year
4. **GOOGLE SCHOLAR** publications → Use as supplementary

### STEP 4: FORMAT OUTPUT (MANDATORY FIELDS)

For EACH valid publication, YOU MUST include ALL these fields:

**Journal Articles:**
- **[Full Paper Title]**
  - Authors: [List all authors with {professor_name} highlighted if present]
  - Journal: [FULL journal name]
  - Year: [Publication year]
  - DOI/Link: [If available]
  - Citations: [If available]
  - Source: [UI Scholar / Database / Google Scholar]

**Conference Papers:**
- **[Full Paper Title - REJECT if only conference name without paper title]**
  - Authors: [MUST list authors]
  - Conference: [FULL conference name with location]
  - Year: [MUST have year]
  - Pages: [If available]
  - Source: [UI Scholar / Database / Google Scholar]

**🚨 QUALITY GATE:**
Before adding ANY publication, verify:
✅ Has complete paper title (not just "The 18th International Conference...")
✅ Has author list (not just "{professor_name}" alone)
✅ Has year (not "Not available")
✅ Has venue (journal name OR conference name)

❌ REJECT publications like:
- "The 18th International Conference on Quality in Research" (no paper title!)
- "IEEE Conference 2020" (too vague)
- "Publication Title" (no authors, no year)

**Books & Book Chapters:**
[If any books with {professor_name} as author]

**TARGET OUTPUT:**
- Minimum: 10 publications
- Target: 15-20 publications
- Maximum: No limit if all are valid

**EXTRACTION MINDSET:**
- "When in doubt, INCLUDE it" (unless obviously wrong)
- Look for research paper titles, not just venue names
- Accept publications even if author name is partially matched
- Better to have 15 good publications than 3 perfect ones

**QUALITY CHECK:**
After extraction, verify:
- Each entry has: Title + Year + Venue
- Title is specific (not just "Conference 2020")
- At least 10 publications listed (if data available)

If truly no publications found after thorough search: "- Publications not available in sources"

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

**🎯 PRIORITY: Extract these profile URLs from data sources**

Search ALL data sources for these URL patterns:
- **Google Scholar**: Look for "scholar.google.com/citations?user=" → Extract full URL
- **UI Scholar**: Look for "scholar.ui.ac.id/en/persons/" → Extract full URL
- **SINTA**: Look for "sinta.kemdikbud.go.id/authors/profile/" → Extract full URL
- **Scopus**: Look for "scopus.com/authid/detail.uri?authorId=" → Extract Author ID
- **ORCID**: Look for "orcid.org/" → Extract ORCID ID
- **ResearchGate**: Look for "researchgate.net/profile/" → Extract profile URL
- **LinkedIn**: Look for "linkedin.com/in/" → Extract profile URL
- **University Profile**: Look for "ui.ac.id" or "ee.ui.ac.id" → Extract profile page URL

**If profile URLs NOT found in data**: Write "Not available in sources"

## CONTACT & ADDITIONAL INFORMATION
[Any other relevant information not covered above]

---

**FINAL QUALITY CHECKLIST (VERIFY BEFORE SUBMITTING):**

1. ✅ **EDUCATION (ZERO TOLERANCE FOR HALLUCINATION)**:
   - Copied EXACTLY from source data (no invented universities)
   - If found "M.Sc., University of Leeds", did NOT write "University of Wollongong"
   - NO DUPLICATES: Each degree listed only once
   - If "Ir., UI, 1993" and "S.T., UI, 1997" both exist, list BOTH (not duplicate!)
   - But if "M.Sc., Leeds, 1997" appears twice, list only ONCE

2. ✅ **PUBLICATIONS** (MOST CRITICAL SECTION):
   - Extracted 15-20 publications (if available in data)
   - Each publication has ALL mandatory fields: Title + Authors + Year + Venue
   - Paper titles are COMPLETE and SPECIFIC (not just conference names)
   - Example GOOD: "A New Control System Algorithm Based on Predictive Model..."
   - Example BAD: "The 18th International Conference..." (rejected!)
   - Prioritized UI Scholar publications (most reliable)
   - Verified {professor_name}'s name appears in author list or context

3. ✅ **RESEARCH INTERESTS**:
   - Extracted ALL keywords and topics from all sources
   - Listed specific areas (e.g., "IoT", "Smart Grid", "Network Security")

4. ✅ **NO HALLUCINATION**:
   - Every fact is from the data sources
   - No invented degrees, universities, or publication titles
   - Used "Not available" when truly not found

5. ✅ **SCHOLAR LINKS** (NEW REQUIREMENT):
   - Google Scholar profile URL extracted and listed in PERSONAL INFORMATION
   - UI Scholar profile URL extracted if available
   - If Scholar links found, they appear BEFORE email field
   - Email only shown if no Scholar links available

6. ✅ **FORMATTING**:
   - Proper markdown with **bold** and - bullets
   - Professional layout with clear sections
   - All URLs are complete and clickable

**ANTI-HALLUCINATION FINAL CHECK:**
Before submitting, ask yourself:
- "Can I point to the exact line in the data sources where I found this information?"
- "Did I copy education EXACTLY as written?"
- "Did I extract at least 10 publications if the data had them?"

If answer is YES to all → Submit the CV
If answer is NO → Go back and fix it

**🎯 PUBLICATION FORMAT EXAMPLES (FOLLOW EXACTLY):**

✅ GOOD PUBLICATION FORMATS:
```
- **IoT-Based Smart Home Energy Management with Machine Learning Optimization**
  - Authors: Riri Fitri Sari, John Doe, Jane Smith
  - Journal: IEEE Internet of Things Journal
  - Year: 2023
  - DOI: 10.1109/JIOT.2023.1234567
  - Citations: 45
  - Source: UI Scholar

- **Deep Learning for Network Traffic Classification and Anomaly Detection**
  - Authors: R.F. Sari, A. Kumar, B. Chen
  - Conference: IEEE International Conference on Communications (ICC) 2022, Seoul, Korea
  - Year: 2022
  - Pages: 1234-1239
  - Source: Google Scholar
```

❌ BAD FORMATS (REJECT THESE):
```
DOI/Link: https://repository.uniga.ac.id/file/... → NO! This is NOT a publication title!
The 18th International Conference on Quality in Research → NO! This is ONLY conference name, WHERE IS THE PAPER TITLE?
Teknologi Berbasis Serbuk: Pilar Manufaktur... → NO! Missing authors, year, venue!
```

Now generate the ACCURATE, COMPREHENSIVE, FACT-CHECKED CV:"""

    try:
        response = llm.call([{"role": "user", "content": prompt}])
        cv_text = str(response).strip()
        
        # Validate response
        if not cv_text or len(cv_text) < 100:
            raise ValueError("LLM returned insufficient content")
        
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
