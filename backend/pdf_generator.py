from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from jinja2 import Environment, FileSystemLoader
import os
import re
from datetime import datetime
from io import BytesIO

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

def create_profile_pdf(profile_data: str) -> bytes:
    """Generate simple profile PDF using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#D70000'),
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Check Please Report", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Clean and format the profile data
    cleaned_data = profile_data.replace('\n', '<br/>')
    story.append(Paragraph(cleaned_data, styles['BodyText']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.read()

def parse_markdown_cv(markdown_text: str) -> dict:
    """
    Parse markdown-formatted CV data from CrewAI agents.
    Handles markdown structure like ## SECTION and bullet points.
    """
    print(f"[MARKDOWN PARSER] Parsing {len(markdown_text)} chars of markdown CV...")
    
    cv_data = {
        'name': 'Unknown',
        'title': '',
        'affiliation': 'Universitas Indonesia',
        'department': 'Departemen Teknik Elektro',
        'email': '',
        'birth_info': '',
        'research_areas': [],
        'education': [],
        'positions': [],
        'publications': [],
        'sinta_score': '',
        'google_scholar': '',
        'scopus': '',
        'generated_date': datetime.now().strftime('%d %B %Y'),
        'family_info': ''
    }
    
    # Remove markdown code fences if present
    markdown_text = re.sub(r'```markdown\s*', '', markdown_text)
    markdown_text = re.sub(r'```\s*$', '', markdown_text)
    
    lines = markdown_text.split('\n')
    current_section = None
    
    def is_valid_data(text: str) -> bool:
        """Check if data is valid (not 'not available' or empty)."""
        invalid_phrases = ['not available', 'information not available', 'n/a', 'none', '-']
        text_lower = text.lower().strip()
        return text_lower and len(text_lower) > 3 and not any(phrase in text_lower for phrase in invalid_phrases)
    
    current_subsection = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Parse main title (# Name)
        if line.startswith('# '):
            cv_data['name'] = line[2:].strip()
            print(f"[MARKDOWN PARSER] ✓ Name: {cv_data['name']}")
            continue
        
        # Parse section headers (## SECTION)
        if line.startswith('## '):
            current_section = line[3:].strip().upper()
            current_subsection = None
            print(f"[MARKDOWN PARSER] → Section: {current_section}")
            continue
        
        # Parse subsection headers (### Subsection)
        if line.startswith('### '):
            current_subsection = line[4:].strip().upper()
            print(f"[MARKDOWN PARSER]   → Subsection: {current_subsection}")
            continue
        
        # Parse bullet points and values based on section/subsection
        if current_section == 'PERSONAL INFORMATION':
            if line.startswith('- **Position'):
                title = line.split(':', 1)[1].strip() if ':' in line else ''
                if is_valid_data(title):
                    cv_data['title'] = title
            elif line.startswith('- **Affiliation'):
                affiliation = line.split(':', 1)[1].strip() if ':' in line else ''
                if is_valid_data(affiliation):
                    cv_data['affiliation'] = affiliation
            elif line.startswith('- **Department'):
                dept = line.split(':', 1)[1].strip() if ':' in line else ''
                if is_valid_data(dept):
                    cv_data['department'] = dept
            elif line.startswith('- **Born'):
                birth = line.split(':', 1)[1].strip() if ':' in line else ''
                if is_valid_data(birth):
                    cv_data['birth_info'] = birth
            elif line.startswith('- **Email'):
                email = line.split(':', 1)[1].strip() if ':' in line else ''
                if is_valid_data(email):
                    cv_data['email'] = email
        
        elif current_section == 'ACADEMIC BACKGROUND':
            # Handle "### Education History" subsection
            if current_subsection == 'EDUCATION HISTORY' or current_section == 'ACADEMIC BACKGROUND':
                if line.startswith('- **'):
                    # Format: "- **Degree** - Institution, Year"
                    edu = line[2:].strip()
                    edu = re.sub(r'\*\*([^*]+)\*\*', r'\1', edu)  # Remove bold
                    if is_valid_data(edu):
                        cv_data['education'].append(edu)
        
        elif current_section == 'EDUCATION':
            # Legacy format support
            if line.startswith('- '):
                edu = line[2:].strip()
                if is_valid_data(edu):
                    cv_data['education'].append(edu)
        
        elif current_section in ['CURRENT POSITIONS', 'CURRENT POSITIONS & ROLES']:
            if line.startswith('- '):
                pos = line[2:].strip()
                pos = re.sub(r'\*\*([^*]+)\*\*', r'\1', pos)  # Remove bold
                if is_valid_data(pos):
                    cv_data['positions'].append(pos)
        
        elif current_section in ['RESEARCH INTERESTS', 'RESEARCH INTERESTS & EXPERTISE']:
            # Handle both direct bullets and subsections (Primary Areas, Specialized Topics, etc)
            if line.startswith('- '):
                research = line[2:].strip()
                research = re.sub(r'\*\*([^*]+)\*\*', r'\1', research)  # Remove bold
                if is_valid_data(research):
                    cv_data['research_areas'].append(research)
        
        elif current_section in ['PUBLICATIONS', 'PUBLICATIONS & SCHOLARLY WORKS']:
            # Support multiple formats:
            # 1. Numbered list: "1. Title (Year)"
            # 2. Bullet with bold: "- **Title** - Authors, Journal (Year)"
            # 3. Under subsections: "### Journal Articles", "### Conference Papers"
            
            if re.match(r'^\d+\.', line):  # Numbered list
                pub = re.sub(r'^\d+\.\s*', '', line).strip()
                pub = re.sub(r'\*\*([^*]+)\*\*', r'\1', pub)  # Remove bold
                if is_valid_data(pub) and len(pub) > 15:
                    cv_data['publications'].append(pub)
            elif line.startswith('- '):
                pub = line[2:].strip()
                pub = re.sub(r'\*\*([^*]+)\*\*', r'\1', pub)  # Remove bold
                if is_valid_data(pub) and len(pub) > 15:
                    cv_data['publications'].append(pub)
        
        elif current_section in ['ACADEMIC METRICS', 'ACADEMIC METRICS & IMPACT']:
            if 'SINTA Score:' in line or 'sinta score:' in line.lower():
                score_match = re.search(r'SINTA Score[:\s]+([0-9.]+)', line, re.IGNORECASE)
                if score_match:
                    cv_data['sinta_score'] = score_match.group(1)
            elif 'H-Index:' in line or 'h-index:' in line.lower():
                h_match = re.search(r'H-Index[:\s]+([0-9]+)', line, re.IGNORECASE)
                if h_match:
                    cv_data['google_scholar'] = f"H-Index: {h_match.group(1)}"
            elif 'Citations:' in line or 'Total Citations:' in line:
                citations_match = re.search(r'Citations[:\s]+([0-9,]+)', line, re.IGNORECASE)
                if citations_match:
                    if cv_data['google_scholar']:
                        cv_data['google_scholar'] += f", Citations: {citations_match.group(1)}"
                    else:
                        cv_data['google_scholar'] = f"Citations: {citations_match.group(1)}"
        
        elif current_section in ['EXTERNAL PROFILES', 'EXTERNAL PROFILES & LINKS']:
            if 'SINTA:' in line:
                url_match = re.search(r'https?://[^\s]+', line)
                if url_match:
                    cv_data['sinta_url'] = url_match.group(0)
            elif 'Google Scholar:' in line or 'Scholar:' in line:
                url_match = re.search(r'https?://[^\s]+', line)
                if url_match:
                    cv_data['scholar_url'] = url_match.group(0)
    
    print(f"[MARKDOWN PARSER] Parsing complete!")
    print(f"  - Name: {cv_data['name']}")
    print(f"  - Title: {cv_data['title']}")
    print(f"  - Education: {len(cv_data['education'])} items")
    print(f"  - Positions: {len(cv_data['positions'])} items")
    print(f"  - Research areas: {len(cv_data['research_areas'])} items")
    print(f"  - Publications: {len(cv_data['publications'])} items")
    
    return cv_data

def extract_info_from_conversation(conversation: str) -> dict:
    """Extract structured information from chat conversation."""
    print(f"[CV PARSER] Extracting from conversation: {len(conversation)} chars")
    
    info = {
        'name': '',
        'title': '',
        'birth_info': '',
        'education': [],
        'positions': [],
        'research_focus': [],
        'publications': [],
        'family': ''
    }
    
    # Extract name from conversation (look for full name pattern)
    name_match = re.search(r'(?:Prof\.\s*)?(?:Dr\.\s*)?(?:Ir\.\s*)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\s*,\s*(?:M\.M\.|M\.Sc|M\.T|Ph\.D))*', conversation)
    if name_match:
        info['name'] = name_match.group(0).strip()
    
    # Extract birth information
    birth_match = re.search(r'born on ([^,]+, \d{4})', conversation, re.IGNORECASE)
    if birth_match:
        info['birth_info'] = birth_match.group(1)
    
    birth_place = re.search(r'born (?:on [^,]+, \d{4}, )?in ([^.]+)', conversation, re.IGNORECASE)
    if birth_place:
        info['birth_info'] += f" in {birth_place.group(1)}"
    
    # Extract education
    education_patterns = [
        r'obtained (?:her|his) degrees from ([^.]+)',
        r'graduated from ([^.]+)',
        r'(?:PhD|Master|Bachelor) (?:from|at) ([^.]+)'
    ]
    for pattern in education_patterns:
        matches = re.findall(pattern, conversation, re.IGNORECASE)
        info['education'].extend(matches)
    
    # Extract positions/roles
    position_patterns = [
        r'(?:is|works as|serves as) (?:the |an? )?([A-Z][^.]+(?:at|of) [^.]+)',
        r'(?:Chairperson|Head|Director|Professor) (?:of|at) ([^.]+)',
    ]
    for pattern in position_patterns:
        matches = re.findall(pattern, conversation)
        info['positions'].extend([m.strip() for m in matches if len(m) > 10])
    
    # Extract research focus
    research_patterns = [
        r'(?:research focuses on|specializes in|expertise in) ([^.]+)',
        r'known for (?:her|his) work (?:in|on) ([^.]+)',
    ]
    for pattern in research_patterns:
        matches = re.findall(pattern, conversation, re.IGNORECASE)
        info['research_focus'].extend(matches)
    
    # Extract publications (look for quoted titles)
    pub_pattern = r'"([^"]{20,})"[\s\(]*(\d{4})?'
    publications = re.findall(pub_pattern, conversation)
    info['publications'] = [(title, year) for title, year in publications if year]
    
    # Extract family information
    family_match = re.search(r'(?:married to|spouse:) ([^.]+)', conversation, re.IGNORECASE)
    if family_match:
        info['family'] = family_match.group(1)
    
    children_match = re.search(r'has (\w+) children', conversation, re.IGNORECASE)
    if children_match:
        info['family'] += f", {children_match.group(1)} children"
    
    print(f"[CV PARSER] Extracted: name={bool(info['name'])}, edu={len(info['education'])}, pos={len(info['positions'])}, pubs={len(info['publications'])}")
    return info

def parse_cv_data(raw_data: str, conversation_data: str = None) -> dict:
    """
    Parse CV data - detects if it's markdown format or raw text.
    """
    print(f"\n[CV PARSER] Starting to parse data...")
    print(f"[CV PARSER] Raw data: {len(raw_data)} chars")
    
    # CHECK 1: Is it markdown format from CrewAI?
    if '## PERSONAL INFORMATION' in raw_data or '## EDUCATION' in raw_data:
        print("[CV PARSER] ✓ Detected markdown format from CrewAI agents!")
        return parse_markdown_cv(raw_data)
    
    # CHECK 2: Use conversation data if available
    if conversation_data:
        print("[CV PARSER] Using conversation extraction...")
        conv_info = extract_info_from_conversation(conversation_data)
        
        if conv_info['name']:
            cv_data = {
                'name': conv_info['name'],
                'title': 'Professor' if 'Prof' in conv_info['name'] else 'Lecturer',
                'affiliation': 'Universitas Indonesia',
                'department': 'Departemen Teknik Elektro',
                'email': '',
                'birth_info': conv_info['birth_info'],
                'research_areas': conv_info['research_focus'],
                'education': conv_info['education'],
                'positions': conv_info['positions'],
                'publications': [f'"{title}" ({year})' for title, year in conv_info['publications']],
                'sinta_score': '',
                'generated_date': datetime.now().strftime('%d %B %Y'),
                'family_info': conv_info['family']
            }
            return cv_data
    
    # CHECK 3: Fallback - basic parsing
    print("[CV PARSER] Using fallback basic parsing...")
    cv_data = {
        'name': 'Unknown',
        'title': 'Professor' if 'Prof' in raw_data else 'Lecturer',
        'affiliation': 'Universitas Indonesia',
        'department': 'Departemen Teknik Elektro',
        'email': '',
        'birth_info': '',
        'research_areas': [],
        'education': [],
        'positions': [],
        'publications': [],
        'sinta_score': '',
        'generated_date': datetime.now().strftime('%d %B %Y'),
        'family_info': ''
    }
    
    # Extract name
    name_patterns = [
        r'(?:Prof\.\s*)?(?:Dr\.\s*)?(?:Ir\.\s*)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, raw_data)
        if match:
            candidate = match.group(0).strip()
            if len(candidate.split()) >= 2:
                cv_data['name'] = candidate
                break
    
    return cv_data

def create_cv_pdf(profile_data: str, conversation_context: str = None) -> bytes:
    """
    Generate a professional academic CV in PDF format using ReportLab.
    Enhanced to handle markdown data from CrewAI agents.
    """
    print(f"\n[CV PDF] Starting CV generation...")
    print(f"[CV PDF] Profile data length: {len(profile_data)} characters")
    print(f"[CV PDF] Conversation length: {len(conversation_context) if conversation_context else 0} characters")
    
    # Parse structured CV data
    cv_data = parse_cv_data(profile_data, conversation_context)
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=50
    )
    
    # Container for PDF elements
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CVTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1a1a1a'),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'CVSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=HexColor('#D70000'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    affiliation_style = ParagraphStyle(
        'CVAffiliation',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    section_title_style = ParagraphStyle(
        'CVSectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#D70000'),
        fontName='Helvetica-Bold',
        spaceBefore=15,
        spaceAfter=10,
        borderWidth=1,
        borderColor=HexColor('#D4AF37'),
        borderPadding=5
    )
    
    body_style = ParagraphStyle(
        'CVBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    # Header
    story.append(Paragraph(cv_data['name'].upper(), title_style))
    story.append(Paragraph(cv_data['title'], subtitle_style))
    story.append(Paragraph(f"{cv_data['department']}, {cv_data['affiliation']}", affiliation_style))
    
    # Birth Info
    if cv_data.get('birth_info'):
        story.append(Paragraph(f"<b>Born:</b> {cv_data['birth_info']}", body_style))
    
    # Contact info
    if cv_data.get('email'):
        story.append(Paragraph(f"<b>Email:</b> {cv_data['email']}", body_style))
    
    if cv_data.get('family_info'):
        story.append(Paragraph(f"<b>Family:</b> {cv_data['family_info']}", body_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Metrics
    if cv_data.get('sinta_score'):
        story.append(Paragraph(f"<b>SINTA Score:</b> {cv_data['sinta_score']}", body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Positions
    if cv_data.get('positions') and len(cv_data['positions']) > 0:
        story.append(Paragraph("CURRENT POSITIONS", section_title_style))
        for pos in cv_data['positions'][:5]:
            cleaned_pos = pos.replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(f"• {cleaned_pos}", body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Research Areas
    if cv_data.get('research_areas') and len(cv_data['research_areas']) > 0:
        story.append(Paragraph("RESEARCH INTERESTS", section_title_style))
        for area in cv_data['research_areas'][:8]:
            cleaned_area = area.replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(f"• {cleaned_area}", body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Education
    if cv_data.get('education') and len(cv_data['education']) > 0:
        story.append(Paragraph("EDUCATION", section_title_style))
        for edu in cv_data['education'][:5]:
            cleaned_edu = edu.replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(f"• {cleaned_edu}", body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Publications
    if cv_data.get('publications') and len(cv_data['publications']) > 0:
        story.append(Paragraph("SELECTED PUBLICATIONS", section_title_style))
        for i, pub in enumerate(cv_data['publications'][:10], 1):
            pub_clean = pub.replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(f"{i}. {pub_clean}", body_style))
        
        if len(cv_data['publications']) > 10:
            story.append(Paragraph(
                f"<i>... and {len(cv_data['publications']) - 10} more publications</i>",
                body_style
            ))
        story.append(Spacer(1, 0.2*inch))
    
    # Check if we have enough data
    total_items = (
        len(cv_data.get('research_areas', [])) + 
        len(cv_data.get('publications', [])) + 
        len(cv_data.get('education', [])) +
        len(cv_data.get('positions', []))
    )
    
    if total_items < 3:
        story.append(Paragraph("NOTE", section_title_style))
        story.append(Paragraph(
            "This CV was generated based on available information from the conversation and database. "
            "For more comprehensive information, please visit the official university website or contact the faculty directly.",
            body_style
        ))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'CVFooter',
        parent=styles['Normal'],
        fontSize=8,
        textColor=HexColor('#999999'),
        alignment=TA_CENTER
    )
    story.append(Paragraph("Curriculum Vitae generated by Check Please AI System", footer_style))
    story.append(Paragraph(f"Generated on: {cv_data['generated_date']}", footer_style))
    story.append(Paragraph("Based on conversation data and academic database sources", footer_style))
    
    # Build PDF
    print("[CV PDF] Building PDF document...")
    doc.build(story)
    
    # Get PDF bytes
    buffer.seek(0)
    pdf_bytes = buffer.read()
    
    print(f"[CV PDF] ✓ PDF generated successfully: {len(pdf_bytes)} bytes")
    print(f"[CV PDF] ✓ Included {total_items} structured data items")
    return pdf_bytes
