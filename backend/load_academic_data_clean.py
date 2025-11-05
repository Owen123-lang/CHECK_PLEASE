import os
import time
from astrapy import DataAPIClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import re
from urllib.parse import urlparse

print("=" * 60)
print("ACADEMIC PROFILE DATA LOADER - SMART DEDUPLICATION")
print("Departemen Teknik Elektro - Universitas Indonesia")
print("=" * 60)

load_dotenv()

# Configuration
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_NAMESPACE = os.getenv("ASTRA_DB_NAMESPACE", "default_keyspace")
ASTRA_DB_COLLECTION = os.getenv("ASTRA_DB_COLLECTION", "academic_profiles_ui")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not all([ASTRA_DB_API_ENDPOINT, ASTRA_DB_APPLICATION_TOKEN, GEMINI_API_KEY]):
    raise ValueError("Missing required environment variables. Check your .env file.")

# ONLY RELIABLE SOURCES - Organized by type
reliable_sources = {
    # Main Department Pages
    'department_pages': [
        'https://ee.ui.ac.id/staff-pengajar/',
        'https://ee.ui.ac.id/professor/',
        'https://ee.ui.ac.id/lecturer/',
        'https://www.eng.ui.ac.id/departemen-teknik-elektro/',
    ],
    
    # Individual Professor Profiles
    'professor_profiles': [
        'https://scholar.ui.ac.id/en/persons/benyamin-kusumo-putro/',
        'https://scholar.ui.ac.id/en/persons/dadang-gunawan/',
        'https://scholar.ui.ac.id/en/persons/eko-tjipto-rahardjo/',
        'https://scholar.ui.ac.id/en/persons/rinaldy/',
        'https://scholar.ui.ac.id/en/persons/nji-raden-poespawati/',
        'https://scholar.ui.ac.id/en/persons/iwa-garniwa-m-k/',
        'https://scholar.ui.ac.id/en/persons/kalamullah-ramli/',
        'https://scholar.ui.ac.id/en/persons/riri-fitri-sari/',
        'https://scholar.ui.ac.id/en/persons/fitri-yuli-zulkifli/',
        'https://scholar.ui.ac.id/en/persons/retno-wigajatri-purnamaningsih/',
        'https://scholar.ui.ac.id/en/persons/anak-agung-putri-ratna/',
        'https://scholar.ui.ac.id/en/persons/muhamad-asvial/',
        'https://scholar.ui.ac.id/en/persons/muhammad-suryanegara/',
        'https://scholar.ui.ac.id/en/persons/gunawan-wibisono/',
        'https://scholar.ui.ac.id/en/persons/feri-yusivar/',
        'https://scholar.ui.ac.id/en/persons/arief-udhiarto/',
        'https://scholar.ui.ac.id/en/persons/purnomo-sidi-priambodo/',
        'https://scholar.ui.ac.id/en/persons/dodi-sudiana/',
        'https://scholar.ui.ac.id/en/persons/aries-subiantoro/',
        'https://scholar.ui.ac.id/en/persons/basari/',
        'https://scholar.ui.ac.id/en/persons/catur-apriono/',
        'https://scholar.ui.ac.id/en/persons/tomy-abuzairi/',
        'https://scholar.ui.ac.id/en/persons/ajib-setyo-arifin/',
        'https://scholar.ui.ac.id/en/persons/prima-dewi-purnamasari/',
        'https://scholar.ui.ac.id/en/persons/mia-rizkinia/',
        'https://scholar.ui.ac.id/en/persons/ruki-harwahyu/',
        'https://scholar.ui.ac.id/en/persons/siti-fauziyah-rahman/',
        'https://scholar.ui.ac.id/en/persons/abdul-halim/',
        'https://scholar.ui.ac.id/en/persons/muhammad-salman/',
        'https://scholar.ui.ac.id/en/persons/fransiskus-astha-ekadiyanto/',
        'https://scholar.ui.ac.id/en/persons/eko-adhi-setiawan/',
        'https://scholar.ui.ac.id/en/persons/abdul-muis/',
        'https://scholar.ui.ac.id/en/persons/budi-sudiarto/',
        'https://scholar.ui.ac.id/en/persons/yan-maraden/',
        'https://scholar.ui.ac.id/en/persons/aji-nur-widyanto/',
        'https://scholar.ui.ac.id/en/persons/i-gde-dharma-nugraha/',
        'https://scholar.ui.ac.id/en/persons/chairul-hudaya/',
        'https://scholar.ui.ac.id/en/persons/taufiq-alif-kurniawan/',
        'https://scholar.ui.ac.id/en/persons/puspita-anggraini-katili/',
        'https://scholar.ui.ac.id/en/persons/faiz-husnayain/',
        'https://scholar.ui.ac.id/en/persons/alfan-presekal/',
        'https://scholar.ui.ac.id/en/persons/nur-imaniati-sumantri/',
    ],
    
    # External Sources
    'external_sources': [
        'https://scholar.google.com/citations?user=o4Tz7vAAAAAJ&hl=id',  # Prof. Riri
        'https://scholar.google.com/citations?user=L2vfAooAAAAJ&hl=id',  # Dr. Suryanegara
        'https://id.wikipedia.org/wiki/Riri_Fitri_Sari',
        'https://sinta.kemdikbud.go.id/affiliations/detail?id=147&view=authors',
    ],
    
    # Collaborative Publications (will be deduplicated automatically)
    'publications': [
        'https://scholar.ui.ac.id/en/publications/failure-mode-classification-of-wind-turbine-gearbox-utilizing-mac/',
        'https://scholar.ui.ac.id/en/publications/autonomous-human-and-animal-classification-using-synthetic-2d-ten/',
        'https://scholar.ui.ac.id/en/publications/hardware-in-the-loop-simulation-of-autonomous-system-using-neural/',
        'https://scholar.ui.ac.id/en/publications/improving-wind-turbine-gearbox-reliability-a-hybrid-deep-learning/',
        'https://scholar.ui.ac.id/en/publications/carbon-reduction-and-social-costbenefit-analysis-of-shore-side-el/',
        # ... (rest of publications)
    ]
}

# Flatten all URLs into single list
all_sources = []
for category, urls in reliable_sources.items():
    all_sources.extend(urls)

print(f"\n📊 Total URLs to process: {len(all_sources)}")
print(f"   - Department pages: {len(reliable_sources['department_pages'])}")
print(f"   - Professor profiles: {len(reliable_sources['professor_profiles'])}")
print(f"   - External sources: {len(reliable_sources['external_sources'])}")
print(f"   - Publications: {len(reliable_sources.get('publications', []))}")

# ============================================
# NEW FEATURE 1: URL DEDUPLICATION TRACKER
# ============================================
scraped_urls = set()  # Track URLs already scraped
url_to_content = {}   # Cache: URL -> content (avoid re-scraping)

def is_duplicate_url(url: str) -> bool:
    """Check if URL was already scraped."""
    return url in scraped_urls

def mark_url_as_scraped(url: str, content: str):
    """Mark URL as scraped and cache content."""
    scraped_urls.add(url)
    url_to_content[url] = content

# ============================================
# NEW FEATURE 2: AUTHOR EXTRACTION
# ============================================
def extract_author_from_url(url: str) -> str:
    """
    Extract author name from scholar.ui.ac.id person URLs.
    Example: 
    https://scholar.ui.ac.id/en/persons/benyamin-kusumo-putro/ 
    -> "Benyamin Kusumo Putro"
    """
    person_pattern = r'/persons/([^/]+)/'
    match = re.search(person_pattern, url)
    
    if match:
        slug = match.group(1)
        # Convert slug to proper name: "benyamin-kusumo-putro" -> "Benyamin Kusumo Putro"
        name = slug.replace('-', ' ').title()
        return name
    
    return "Unknown Author"

def is_publication_url(url: str) -> bool:
    """Check if URL is a publication page."""
    return '/publications/' in url

def is_person_url(url: str) -> bool:
    """Check if URL is a person profile page."""
    return '/persons/' in url

# ============================================
# NEW FEATURE 3: COLLABORATIVE RESEARCH DETECTION
# ============================================
def detect_collaborative_authors(url: str, content: str) -> list:
    """
    Detect multiple authors from publication page content.
    Returns list of author names.
    """
    authors = []
    
    # Pattern 1: Look for "Authors:" section
    authors_section = re.search(r'Authors?[:\s]+([^\n]+)', content, re.IGNORECASE)
    if authors_section:
        author_text = authors_section.group(1)
        # Split by common delimiters
        potential_authors = re.split(r'[,;]', author_text)
        authors.extend([a.strip() for a in potential_authors if len(a.strip()) > 3])
    
    # Pattern 2: Look for name patterns (Prof., Dr., etc.)
    name_pattern = r'(?:Prof\.|Dr\.|Ir\.)\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+'
    found_names = re.findall(name_pattern, content)
    authors.extend(found_names)
    
    # Remove duplicates and clean
    authors = list(set([a.strip() for a in authors if len(a.strip()) > 5]))
    
    return authors[:10]  # Max 10 authors to avoid noise

print("\n[1/6] Connecting to Astra DB...")
client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)
print("✓ Connected to Astra DB")

print(f"\n[2/6] Setting up collection: {ASTRA_DB_COLLECTION}...")
try:
    collection = db.get_collection(ASTRA_DB_COLLECTION)
    print(f"✓ Using existing collection: {ASTRA_DB_COLLECTION}")
except Exception as e:
    print(f"✗ Collection error: {e}")
    print("Please create the collection via Astra DB UI first!")
    exit(1)

print("\n[3/6] CLEARING OLD DATA...")
print("⚠️  This will delete ALL existing documents in the collection!")
confirm = input("Type 'YES' to confirm deletion: ")

if confirm == 'YES':
    try:
        result = collection.delete_many({})
        print(f"✓ Deleted old documents")
    except Exception as e:
        print(f"✗ Error clearing collection: {e}")
else:
    print("✗ Aborted. Exiting...")
    exit(0)

print("\n[4/6] Initializing Google Gemini Embeddings...")
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)
print("✓ Embeddings model ready")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=200,
)

def is_valid_content(text: str) -> bool:
    """Validate that scraped content is actually useful."""
    error_indicators = [
        '<!DOCTYPE html>',
        '<div class="error',
        '404',
        'not found',
        'error occurred'
    ]
    
    text_lower = text.lower()
    for indicator in error_indicators:
        if indicator.lower() in text_lower:
            return False
    
    valid_indicators = [
        'prof', 'dr.', 'profesor', 'lecture', 'dosen',
        'research', 'publikasi', 'departemen', 'teknik elektro'
    ]
    
    valid_count = sum(1 for indicator in valid_indicators if indicator in text_lower)
    return valid_count >= 2 and len(text) > 200

def scrape_page(url: str) -> dict:
    """
    Scrape content from a webpage with SMART DEDUPLICATION.
    Returns: {
        'content': str,
        'author': str,
        'authors': list,  # For collaborative research
        'is_collaborative': bool
    }
    """
    
    # ============================================
    # DEDUPLICATION CHECK
    # ============================================
    if is_duplicate_url(url):
        print(f"    ⏭️  SKIPPED (already scraped)")
        return None
    
    try:
        print(f"  → Scraping: {url}")
        loader = WebBaseLoader([url])
        docs = loader.load()
        
        if docs:
            raw_text = re.sub(r'<[^>]*>', '', docs[0].page_content)
            cleaned_text = ' '.join(raw_text.split())
            
            if is_valid_content(cleaned_text):
                # Extract metadata
                author = extract_author_from_url(url)
                is_pub = is_publication_url(url)
                
                # Detect collaborative authors (for publications)
                authors = []
                is_collaborative = False
                if is_pub:
                    authors = detect_collaborative_authors(url, cleaned_text)
                    is_collaborative = len(authors) > 1
                
                # Mark as scraped
                mark_url_as_scraped(url, cleaned_text)
                
                # Logging
                status_icon = "👥" if is_collaborative else "✓"
                print(f"    {status_icon} Scraped {len(cleaned_text)} characters (VALID)")
                if is_collaborative:
                    print(f"    📚 Collaborative research: {len(authors)} authors detected")
                    print(f"       {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
                
                return {
                    'content': cleaned_text,
                    'author': author,
                    'authors': authors,
                    'is_collaborative': is_collaborative,
                    'url_type': 'publication' if is_pub else 'profile'
                }
            else:
                print(f"    ✗ Content validation failed")
                return None
        else:
            print(f"    ✗ No content found")
            return None
    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
        return None

print("\n[5/6] Scraping with SMART DEDUPLICATION...")
print("-" * 60)
print("🔍 Features:")
print("   ✅ Skip duplicate URLs automatically")
print("   ✅ Detect collaborative research (multiple authors)")
print("   ✅ Extract author metadata from URLs")
print("-" * 60)

total_chunks = 0
successful_sources = 0
skipped_duplicates = 0

for idx, url in enumerate(all_sources, 1):
    print(f"\n[{idx}/{len(all_sources)}] Processing: {url}")
    
    result = scrape_page(url)
    
    if not result:
        if is_duplicate_url(url):
            skipped_duplicates += 1
        continue
    
    content = result['content']
    chunks = splitter.split_text(content)
    print(f"  → Split into {len(chunks)} chunks")
    
    # Insert chunks with RICH METADATA
    inserted_count = 0
    for i, chunk in enumerate(chunks, 1):
        try:
            vector = embeddings.embed_query(chunk)
            
            # ============================================
            # RICH METADATA STORAGE
            # ============================================
            doc = {
                "$vector": vector,
                "text": chunk,
                "source_url": url,
                "chunk_index": i,
                "timestamp": time.time(),
                # NEW: Author metadata
                "primary_author": result['author'],
                "is_collaborative": result['is_collaborative'],
                "url_type": result['url_type']
            }
            
            # Add collaborative authors if available
            if result['is_collaborative'] and result['authors']:
                doc['collaborative_authors'] = result['authors']
            
            collection.insert_one(doc)
            
            inserted_count += 1
            total_chunks += 1
            
            if i % 5 == 0:
                print(f"    → Inserted {i}/{len(chunks)} chunks...")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ✗ Error inserting chunk {i}: {str(e)}")
            continue
    
    if inserted_count > 0:
        successful_sources += 1
        print(f"  ✓ Successfully inserted {inserted_count} chunks")
    
    if idx < len(all_sources):
        time.sleep(2)

print("\n" + "=" * 60)
print("[6/6] DATA LOADING COMPLETE!")
print("=" * 60)
print(f"✓ Total chunks inserted: {total_chunks}")
print(f"✓ Successful sources: {successful_sources}/{len(all_sources)}")
print(f"⏭️  Skipped duplicates: {skipped_duplicates}")
print(f"✓ Collection name: {ASTRA_DB_COLLECTION}")

# Statistics
unique_urls = len(scraped_urls)
print(f"\n📊 DEDUPLICATION STATISTICS:")
print(f"   - Unique URLs processed: {unique_urls}")
print(f"   - Duplicate URLs skipped: {skipped_duplicates}")
print(f"   - Efficiency gain: {(skipped_duplicates/len(all_sources)*100):.1f}% less scraping")

if total_chunks > 0:
    print("\n🎉 Database is ready with CLEAN, DEDUPLICATED data!")
    print("   ✅ No duplicate research papers")
    print("   ✅ Collaborative research properly tagged")
    print("   ✅ Author metadata available for AI queries")
    print("\nYou can now start the backend server.")
else:
    print("\n❌ WARNING: No data was inserted!")
