"""
eng.ui.ac.id Personnel Page Scraper
Specialized scraper for Faculty of Engineering UI personnel pages
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional

def scrape_eng_ui_personnel(professor_name: str) -> Optional[Dict]:
    """
    Scrape personnel page from eng.ui.ac.id
    
    Args:
        professor_name: Name of professor (e.g., "Mia Rizkinia", "Abdul Muis")
    
    Returns:
        Dictionary with structured data or None if not found
    """
    
    # Normalize name for URL
    # Remove titles and degrees: Dr., Dr. Eng., S.T., M.T., M.Eng., Ph.D., etc.
    name_clean = re.sub(r'\b(dr\.?|eng\.?|st\.?|mt\.?|m\.eng\.?|ph\.?d\.?|prof\.?)\b', '', professor_name, flags=re.IGNORECASE)
    name_clean = name_clean.strip()
    
    # Convert to lowercase and remove non-letters
    name_normalized = name_clean.lower()
    name_normalized = re.sub(r'[^a-z\s]', '', name_normalized)
    name_normalized = re.sub(r'\s+', ' ', name_normalized).strip()  # Normalize spaces
    name_normalized = '-'.join(name_normalized.split())  # Replace spaces with hyphens
    
    url = f"https://eng.ui.ac.id/personnel/{name_normalized}/"
    
    print(f"[ENG_UI_SCRAPER] Attempting to scrape: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            print(f"[ENG_UI_SCRAPER] ❌ Page not found (404): {url}")
            return None
        
        if response.status_code != 200:
            print(f"[ENG_UI_SCRAPER] ❌ HTTP {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract data
        data = {
            'name': '',
            'title': '',
            'position': '',
            'education': [],
            'research_expertise': [],
            'publications': [],
            'source_url': url
        }
        
        # Extract name and title
        name_elem = soup.find('h1', class_='entry-title')
        if name_elem:
            data['name'] = name_elem.get_text(strip=True)
        
        # Extract position (Associate Professor, Assistant Professor, etc.)
        position_elem = soup.find('p', string=lambda t: t and ('Professor' in t or 'Lecturer' in t))
        if position_elem:
            data['position'] = position_elem.get_text(strip=True)
        
        # Extract Education section
        education_section = soup.find('h3', string='Education')
        if education_section:
            education_list = education_section.find_next('ul')
            if education_list:
                for item in education_list.find_all('li'):
                    edu_text = item.get_text(strip=True)
                    data['education'].append(edu_text)
        
        # Extract Research Expertise section
        expertise_section = soup.find('h3', string='Research Expertise')
        if expertise_section:
            expertise_text = expertise_section.find_next('p')
            if expertise_text:
                # Split by comma
                expertise_items = expertise_text.get_text(strip=True).split(',')
                data['research_expertise'] = [item.strip() for item in expertise_items if item.strip()]
        
        # Extract Latest Publications
        pub_section = soup.find('h3', string='Latest Publication')
        if pub_section:
            pub_list = pub_section.find_next('ul')
            if pub_list:
                for item in pub_list.find_all('li'):
                    pub_text = item.get_text(strip=True)
                    # Extract year from end (e.g., "...2025")
                    year_match = re.search(r'(\d{4})$', pub_text)
                    year = year_match.group(1) if year_match else None
                    
                    # Remove year from title
                    title = pub_text
                    if year:
                        title = pub_text[:year_match.start()].strip()
                    
                    data['publications'].append({
                        'title': title,
                        'year': year
                    })
        
        print(f"[ENG_UI_SCRAPER] ✅ Successfully scraped:")
        print(f"  - Education: {len(data['education'])} items")
        print(f"  - Research Expertise: {len(data['research_expertise'])} items")
        print(f"  - Publications: {len(data['publications'])} items")
        
        return data
        
    except requests.exceptions.Timeout:
        print(f"[ENG_UI_SCRAPER] ⏱️ Timeout after 10 seconds")
        return None
    except Exception as e:
        print(f"[ENG_UI_SCRAPER] ❌ Error: {e}")
        return None

def format_eng_ui_data(data: Dict) -> str:
    """
    Format scraped data into readable text
    
    Args:
        data: Dictionary from scrape_eng_ui_personnel()
    
    Returns:
        Formatted string
    """
    if not data:
        return "No data available from eng.ui.ac.id"
    
    output = []
    
    output.append(f"=== ENG.UI.AC.ID PERSONNEL DATA ===\n")
    
    if data['name']:
        output.append(f"Name: {data['name']}")
    
    if data['position']:
        output.append(f"Position: {data['position']}")
    
    if data['education']:
        output.append(f"\nEducation:")
        for edu in data['education']:
            output.append(f"  • {edu}")
    
    if data['research_expertise']:
        output.append(f"\nResearch Expertise:")
        for exp in data['research_expertise']:
            output.append(f"  • {exp}")
    
    if data['publications']:
        output.append(f"\nLatest Publications:")
        for i, pub in enumerate(data['publications'], 1):
            title = pub['title']
            year = pub['year'] if pub['year'] else 'Year unknown'
            output.append(f"  {i}. {title} ({year})")
    
    output.append(f"\nSource: {data['source_url']}")
    
    return '\n'.join(output)


# Test function
if __name__ == "__main__":
    print("Testing eng.ui.ac.id Personnel Scraper\n")
    
    # Test with Mia Rizkinia
    print("Test 1: Mia Rizkinia")
    print("-" * 60)
    data1 = scrape_eng_ui_personnel("Dr. Eng. Mia Rizkinia")
    if data1:
        print(format_eng_ui_data(data1))
    print("\n" + "="*60 + "\n")
    
    # Test with Abdul Muis
    print("Test 2: Abdul Muis")
    print("-" * 60)
    data2 = scrape_eng_ui_personnel("Dr. Abdul Muis")
    if data2:
        print(format_eng_ui_data(data2))
    print("\n" + "="*60 + "\n")