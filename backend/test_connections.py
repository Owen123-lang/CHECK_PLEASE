import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

print("=" * 60)
print("TESTING BACKEND CONNECTIONS AND API KEYS")
print("=" * 60)

# Test 1: Check if .env file is loaded
print("\n[TEST 1] Environment Variables")
print("-" * 60)

env_vars = {
    "ASTRA_DB_API_ENDPOINT": os.getenv("ASTRA_DB_API_ENDPOINT"),
    "ASTRA_DB_APPLICATION_TOKEN": os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    "ASTRA_DB_NAMESPACE": os.getenv("ASTRA_DB_NAMESPACE"),
    "ASTRA_DB_COLLECTION": os.getenv("ASTRA_DB_COLLECTION"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY")
}

all_env_ok = True
for key, value in env_vars.items():
    if value:
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"✓ {key}: {masked}")
    else:
        print(f"✗ {key}: NOT FOUND")
        all_env_ok = False

if not all_env_ok:
    print("\n❌ ERROR: Some environment variables are missing!")
    sys.exit(1)

# Test 2: Test Gemini API Key
print("\n[TEST 2] Testing Gemini API Connection")
print("-" * 60)
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
    
    # Test embeddings
    print("Testing Google Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    test_embedding = embeddings.embed_query("test")
    print(f"✓ Embeddings working! Vector dimension: {len(test_embedding)}")
    
    # Test LLM
    print("Testing Gemini LLM...")
    from crewai import LLM
    llm = LLM(
        model="gemini/gemini-pro",
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.2
    )
    print("✓ LLM initialized successfully!")
    
except Exception as e:
    print(f"✗ Gemini API Error: {str(e)}")
    sys.exit(1)

# Test 3: Test Astra DB Connection
print("\n[TEST 3] Testing Astra DB Connection")
print("-" * 60)
try:
    from astrapy import DataAPIClient
    
    client = DataAPIClient(os.getenv("ASTRA_DB_APPLICATION_TOKEN"))
    db = client.get_database_by_api_endpoint(os.getenv("ASTRA_DB_API_ENDPOINT"))
    
    print(f"✓ Connected to Astra DB!")
    
    # Test collection access
    collection = db.get_collection(os.getenv("ASTRA_DB_COLLECTION"))
    print(f"✓ Collection '{os.getenv('ASTRA_DB_COLLECTION')}' accessible!")
    
    # Try a simple query
    print("Testing vector search...")
    query_vector = embeddings.embed_query("Formula 1")
    results = collection.find(
        sort={"$vector": query_vector},
        limit=1,
        projection={"text": 1}
    )
    
    docs = list(results)
    if docs:
        print(f"✓ Vector search working! Found {len(docs)} document(s)")
        if 'text' in docs[0]:
            print(f"  Sample text: {docs[0].get('text', '')[:100]}...")
    else:
        print("⚠ Warning: No documents found in collection")
    
except Exception as e:
    print(f"✗ Astra DB Error: {str(e)}")
    sys.exit(1)

# Test 4: Test Tools Import
print("\n[TEST 4] Testing Tools Import")
print("-" * 60)
try:
    from tools import primary_vector_search_tool, dynamic_web_scraper_tool
    print("✓ primary_vector_search_tool imported successfully")
    print("✓ dynamic_web_scraper_tool imported successfully")
except Exception as e:
    print(f"✗ Tools Import Error: {str(e)}")
    sys.exit(1)

# Test 5: Test Agent Core
print("\n[TEST 5] Testing Agent Core")
print("-" * 60)
try:
    from agent_core import run_agentic_rag_crew
    print("✓ Agent core imported successfully")
    
    # Try a simple query
    print("\nTesting simple query: 'test'")
    result = run_agentic_rag_crew("What is Formula 1?", user_urls=None)
    print(f"✓ Query executed successfully!")
    print(f"  Result preview: {str(result)[:200]}...")
    
except Exception as e:
    print(f"✗ Agent Core Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test FastAPI Endpoint
print("\n[TEST 6] Testing FastAPI Main App")
print("-" * 60)
try:
    from main import app
    print("✓ FastAPI app imported successfully")
except Exception as e:
    print(f"✗ FastAPI Import Error: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED! Backend is properly configured.")
print("=" * 60)
print("\n🚀 You can now start the backend server with:")
print("   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
