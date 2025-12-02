"""
SIMPLIFIED CV GENERATION PROMPTS
Separated from cv_agent.py for clarity and maintainability
"""

def get_cv_generation_prompt(professor_name: str, compact_context: str) -> str:
    """
    Generate a CLEAR, DIRECT prompt for CV generation.
    Removes ALL confusion and complexity.
    """
    
    return f"""You are an expert CV data extractor. Extract ALL information from these sources for {professor_name}:

{compact_context}

**CRITICAL EXTRACTION RULES:**

🎯 **RULE 1: DATA SOURCE PRIORITY**
- 🥇 ENG.UI.AC.ID official page (if available) = MOST AUTHORITATIVE
- 🥈 UI SCHOLAR = Primary for publications
- 🥉 GOOGLE SCHOLAR = Secondary for publications
- 🔹 DATABASE = Fallback

🎓 **RULE 2: EDUCATION** (LANGUAGE AGNOSTIC)
Look for these patterns in ANY language (Indonesian OR English):
- Degree words: "Bachelor", "Sarjana", "S.T.", "Master", "Magister", "M.T.", "Doctoral", "Doktor", "Ph.D.", "Dr.Eng"
- University words: "University", "Universitas", "Institut"
- Year: 19XX or 20XX

Extract format: **[Degree]**, [University], [Country], [Year]

Examples from sources:
- "Bachelor, Universitas Indonesia, Indonesia, 2008"
- "Master, Universitas Indonesia, Indonesia, 2011"
- "Doctoral, University of Kitakyushu, Japan, 2018"

📚 **RULE 3: PUBLICATIONS** (MOST CRITICAL - FIX THE BUG!)

**STEP 1: Find publication data**
Scan ALL sources for these patterns:
- Lines with paper titles (usually > 30 characters)
- Lines with years (2015-2025)
- Lines with "Journal:", "Conference:", "Proceedings"
- Author lists with multiple names

**STEP 2: Extract COMPLETE data**
For EACH publication you find, extract:
✅ FULL paper title (the ACTUAL research paper name, NOT just "Source: ENG.UI.AC.ID")
✅ All authors (comma-separated)
✅ Year (YYYY format)
✅ Venue (journal name OR conference name)

**STEP 3: Validation**
❌ REJECT if:
- Only has "Source: ENG.UI.AC.ID" without paper title
- Only has conference name like "Conference on Radar..." without paper title
- Missing year or authors
- Duplicate of already listed publication

✅ ACCEPT if:
- Has SPECIFIC paper title (e.g., "Benchmarking machine learning algorithm for stunting risk prediction in Indonesia")
- Has author list
- Has year
- Has venue (journal/conference)

**STEP 4: Format**
For each valid publication:

**Journal:**
- **[FULL PAPER TITLE]**
  - Authors: [Author1, Author2, Author3, ...]
  - Journal: [Journal Name]
  - Year: [YYYY]
  - Source: [ENG.UI.AC.ID / UI Scholar / Google Scholar]

**Conference:**
- **[FULL PAPER TITLE]**
  - Authors: [Author1, Author2, ...]
  - Conference: [Conference Name with Location]
  - Year: [YYYY]
  - Source: [ENG.UI.AC.ID / UI Scholar / Google Scholar]

**EXAMPLES OF CORRECT EXTRACTION:**

✅ GOOD (has all fields):
- **Benchmarking machine learning algorithm for stunting risk prediction in Indonesia**
  - Authors: N. Novalina, I. A. A. Tarigan, F. K. Kameela, M. Rizkinia
  - Journal: Bulletin of Electrical Engineering and Informatics
  - Year: 2025
  - Source: ENG.UI.AC.ID

✅ GOOD (has all fields):
- **A CNN-RF Hybrid Approach for Rice Paddy Fields Mapping in Indramayu Using Sentinel-1 and Sentinel-2 Data**
  - Authors: D. Sudiana, M. Rizkinia, et al.
  - Journal: Computers
  - Year: 2025
  - Source: ENG.UI.AC.ID

❌ BAD (incomplete - missing title):
- Source: ENG.UI.AC.ID OFFICIAL PERSONNEL PAGE

❌ BAD (incomplete - only conference name, no paper title):
- Conference: International Conference on Radar, Antenna, Microwave...

❌ BAD (incomplete - missing authors and year):
- **Some Paper Title**
  - Journal: IEEE
  
**TARGET:** Extract 10-15 complete publications (if data available)

---

**OUTPUT FORMAT:**

# DR. ENG. {professor_name.upper()}

## PERSONAL INFORMATION
- Position: [Extract from sources]
- Affiliation: Universitas Indonesia
- Department: Departemen Teknik Elektro
- Email: [email@ui.ac.id with @ symbol]
- H-Index: [if available]
- Citations: [if available]

## EDUCATION
- **Doctoral**, [University], [Country], [Year]
- **Master**, [University], [Country], [Year]
- **Bachelor**, [University], [Country], [Year]

## RESEARCH INTERESTS
- [Interest 1]
- [Interest 2]
- [Interest 3]
- [Interest 4]
- [Interest 5]

## SELECTED PUBLICATIONS

[List 10-15 publications following the format above]

---

**FINAL CHECKLIST BEFORE SUBMITTING:**
✅ Education section has 3 entries (Bachelor/Master/Doctoral)
✅ Publications section has 10+ entries
✅ EVERY publication has: Title + Authors + Year + Venue
✅ NO publication is just "Source: ENG.UI.AC.ID" alone
✅ NO publication is just "Conference name" without paper title
✅ Email uses @ symbol (not [at])

Generate the CV now with COMPLETE publication data:"""