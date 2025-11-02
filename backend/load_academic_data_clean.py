import os
import time
from astrapy import DataAPIClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import re

print("=" * 60)
print("ACADEMIC PROFILE DATA LOADER - CLEAN VERSION")
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

# ONLY RELIABLE SOURCES - No Google Scholar (causes 404 errors)
reliable_sources = [
    'https://ee.ui.ac.id/staff-pengajar/',  # Main faculty page
    'https://ee.ui.ac.id/professor/',        # Professors page
    'https://id.wikipedia.org/wiki/Riri_Fitri_Sari',  # Wikipedia backup
]

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
        # Delete all documents
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
    chunk_size=800,  # Larger chunks for better context
    chunk_overlap=200,
)

def is_valid_content(text: str) -> bool:
    """Validate that scraped content is actually useful."""
    # Check for error indicators
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
    
    # Check for academic content indicators
    valid_indicators = [
        'prof', 'dr.', 'profesor', 'lecture', 'dosen',
        'research', 'publikasi', 'departemen', 'teknik elektro'
    ]
    
    valid_count = sum(1 for indicator in valid_indicators if indicator in text_lower)
    
    # Must have at least 2 valid indicators and be long enough
    return valid_count >= 2 and len(text) > 200

def scrape_page(url: str) -> str:
    """Scrape content from a webpage with validation."""
    try:
        print(f"  → Scraping: {url}")
        loader = WebBaseLoader([url])
        docs = loader.load()
        
        if docs:
            # Clean HTML
            raw_text = re.sub(r'<[^>]*>', '', docs[0].page_content)
            # Remove excessive whitespace
            cleaned_text = ' '.join(raw_text.split())
            
            # VALIDATE content before returning
            if is_valid_content(cleaned_text):
                print(f"    ✓ Scraped {len(cleaned_text)} characters (VALID)")
                return cleaned_text
            else:
                print(f"    ✗ Content validation failed (error page or irrelevant)")
                return None
        else:
            print(f"    ✗ No content found")
            return None
    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
        return None

print("\n[5/6] Scraping RELIABLE academic profile data...")
print("-" * 60)

total_chunks = 0
successful_sources = 0

for idx, url in enumerate(reliable_sources, 1):
    print(f"\n[{idx}/{len(reliable_sources)}] Processing: {url}")
    
    content = scrape_page(url)
    
    if not content:
        print(f"  ⚠ Skipping {url} - invalid or no content")
        continue
    
    chunks = splitter.split_text(content)
    print(f"  → Split into {len(chunks)} chunks")
    
    # Insert chunks with rate limiting
    inserted_count = 0
    for i, chunk in enumerate(chunks, 1):
        try:
            # Generate embedding
            vector = embeddings.embed_query(chunk)
            
            # Insert into Astra DB
            collection.insert_one({
                "$vector": vector,
                "text": chunk,
                "source_url": url,
                "chunk_index": i,
                "timestamp": time.time()
            })
            
            inserted_count += 1
            total_chunks += 1
            
            # Progress indicator
            if i % 5 == 0:
                print(f"    → Inserted {i}/{len(chunks)} chunks...")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ✗ Error inserting chunk {i}: {str(e)}")
            continue
    
    if inserted_count > 0:
        successful_sources += 1
        print(f"  ✓ Successfully inserted {inserted_count} chunks from this source")
    
    # Delay between sources
    if idx < len(reliable_sources):
        print(f"  ⏳ Waiting 3 seconds before next source...")
        time.sleep(3)

print("\n" + "=" * 60)
print("[6/6] DATA LOADING COMPLETE!")
print("=" * 60)
print(f"✓ Total chunks inserted: {total_chunks}")
print(f"✓ Successful sources: {successful_sources}/{len(reliable_sources)}")
print(f"✓ Collection name: {ASTRA_DB_COLLECTION}")

if total_chunks > 0:
    print("\n🎉 Database is ready with CLEAN, VALIDATED data!")
    print("You can now start the backend server.")
else:
    print("\n❌ WARNING: No data was inserted!")
    print("Check if the websites are accessible and contain valid academic content.")
