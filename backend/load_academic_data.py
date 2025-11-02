import os
import time
from astrapy import DataAPIClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

print("=" * 60)
print("ACADEMIC PROFILE DATA LOADER")
print("Departemen Teknik Elektro - Universitas Indonesia")
print("=" * 60)

# Load environment variables
load_dotenv()

# Configuration
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_NAMESPACE = os.getenv("ASTRA_DB_NAMESPACE", "default_keyspace")
ASTRA_DB_COLLECTION = "academic_profiles_ui"  # New collection name
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not all([ASTRA_DB_API_ENDPOINT, ASTRA_DB_APPLICATION_TOKEN, GEMINI_API_KEY]):
    raise ValueError("Missing required environment variables. Check your .env file.")

# Academic data sources for scraping
academicData = [
    'https://www.eng.ui.ac.id/departemen-teknik-elektro/',
    'https://scholar.google.com/citations?user=o4Tz7vAAAAAJ&hl=id',  # Prof. Riri Fitri Sari
    'https://scholar.google.com/citations?user=L2vfAooAAAAJ&hl=id',  # Dr. Muhammad Suryanegara
    'https://id.wikipedia.org/wiki/Riri_Fitri_Sari',
    'https://sinta.kemdikbud.go.id/affiliations/detail?id=147&view=authors',  # UI Affiliations
]

# Initialize Astra DB client
print("\n[1/5] Connecting to Astra DB...")
client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)
print("✓ Connected to Astra DB")

# Create or get collection with PROPER vector configuration
print(f"\n[2/5] Setting up collection: {ASTRA_DB_COLLECTION}...")

# Check if collection exists and use it
try:
    collection = db.get_collection(ASTRA_DB_COLLECTION)
    print(f"✓ Using existing collection: {ASTRA_DB_COLLECTION}")
    print("  ⚠ Make sure this collection has vector search enabled (dimension=768, metric=cosine)")
except:
    print(f"✗ Collection '{ASTRA_DB_COLLECTION}' not found!")
    print("\n" + "=" * 60)
    print("MANUAL SETUP REQUIRED:")
    print("=" * 60)
    print("Please create the collection manually via Astra DB Web UI:")
    print(f"1. Go to: {ASTRA_DB_API_ENDPOINT.replace('/api/json/v1', '')}")
    print(f"2. Create a new collection named: {ASTRA_DB_COLLECTION}")
    print("3. Enable Vector Search with these settings:")
    print("   - Embedding generation method: Bring my own")
    print("   - Vector Dimension: 768")
    print("   - Similarity Metric: cosine")
    print("4. Save the collection")
    print("5. Run this script again")
    print("=" * 60)
    exit(1)

# Initialize embedding model
print("\n[3/5] Initializing Google Gemini Embeddings...")
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)
print("✓ Embeddings model ready")

# Initialize text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=100,
)

# Function to scrape and clean webpage
def scrape_page(url: str) -> str:
    """Scrape content from a webpage and clean HTML tags."""
    try:
        print(f"  → Scraping: {url}")
        loader = WebBaseLoader([url])
        docs = loader.load()
        
        if docs:
            # Clean HTML and extract text
            import re
            raw_text = re.sub(r'<[^>]*>', '', docs[0].page_content)
            # Remove excessive whitespace
            cleaned_text = ' '.join(raw_text.split())
            print(f"    ✓ Scraped {len(cleaned_text)} characters")
            return cleaned_text
        else:
            print(f"    ✗ No content found")
            return None
    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
        return None

# Load and process academic data
print("\n[4/5] Scraping and loading academic profile data...")
print("-" * 60)

total_chunks = 0
for idx, url in enumerate(academicData, 1):
    print(f"\n[{idx}/{len(academicData)}] Processing: {url}")
    
    content = scrape_page(url)
    
    if not content:
        print(f"  ⚠ Skipping {url} - no content")
        continue
    
    # Split content into chunks
    chunks = splitter.split_text(content)
    print(f"  → Split into {len(chunks)} chunks")
    
    # Generate embeddings in batches to avoid rate limits
    batch_size = 5
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        
        try:
            # Generate embeddings for batch
            print(f"    → Processing chunks {i+1}-{min(i+batch_size, len(chunks))}...")
            embedding_results = embeddings.embed_documents(batch)
            
            # Insert batch into Astra DB
            for chunk_idx, (chunk, vector) in enumerate(zip(batch, embedding_results), start=i+1):
                try:
                    collection.insert_one({
                        "$vector": vector,
                        "text": chunk,
                        "source_url": url,
                        "chunk_index": chunk_idx
                    })
                    total_chunks += 1
                except Exception as e:
                    print(f"      ✗ Error inserting chunk {chunk_idx}: {str(e)}")
                    continue
            
            # Add delay to avoid rate limits (1 second between batches)
            if i + batch_size < len(chunks):
                time.sleep(1)
                
        except Exception as e:
            print(f"    ✗ Error processing batch: {str(e)}")
            print(f"    ⚠ Waiting 5 seconds before continuing...")
            time.sleep(5)
            continue
    
    print(f"  ✓ Completed processing {url}")
    print(f"    → Total chunks inserted from this source: {total_chunks}")
    
    # Add delay between sources
    if idx < len(academicData):
        print(f"  ⏳ Waiting 3 seconds before next source...")
        time.sleep(3)

# Summary
print("\n" + "=" * 60)
print("[5/5] DATA LOADING COMPLETE!")
print("=" * 60)
print(f"✓ Total chunks inserted: {total_chunks}")
print(f"✓ Collection name: {ASTRA_DB_COLLECTION}")
print(f"✓ Sources processed: {len(academicData)}")
print("\n🎉 Academic profile database is ready!")
print("You can now start the backend server and query the academic profiles.")
