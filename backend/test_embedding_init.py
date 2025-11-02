import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

print("--- Starting Embedding Initialization Test ---")

# 1. Load environment variables from .env file
print("Loading .env file...")
load_dotenv()
print(".env file loaded.")

# 2. Get the API Key from environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in environment variables.")
    print("Please ensure your .env file is in the 'backend' directory and contains the line: GEMINI_API_KEY='your_actual_api_key'")
else:
    print(f"✅ Found GEMINI_API_KEY: '...{api_key[-4:]}'")

# 3. Try to initialize the embedding model
if api_key:
    try:
        print("\nAttempting to initialize GoogleGenerativeAIEmbeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        print("✅ SUCCESS: GoogleGenerativeAIEmbeddings initialized successfully!")
    except Exception as e:
        print(f"\n❌ FAILED to initialize GoogleGenerativeAIEmbeddings.")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Details: {e}")
        print("\n   This is the root cause of the backend server crash.")
        print("   Please check if your GEMINI_API_KEY is correct and has the necessary permissions.")

print("\n--- Test Finished ---")
