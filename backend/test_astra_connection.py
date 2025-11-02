import os
from dotenv import load_dotenv
from astrapy import DataAPIClient

print("--- Starting Astra DB Connection Test ---")

# 1. Load environment variables
print("Loading .env file...")
load_dotenv()
print(".env file loaded.")

# 2. Get Astra DB credentials from environment
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")

if not ASTRA_DB_API_ENDPOINT:
    print("❌ ERROR: ASTRA_DB_API_ENDPOINT not found.")
if not ASTRA_DB_APPLICATION_TOKEN:
    print("❌ ERROR: ASTRA_DB_APPLICATION_TOKEN not found.")

# 3. Try to initialize the DataAPIClient
if ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN:
    try:
        print("\nAttempting to initialize DataAPIClient...")
        client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
        print("✅ SUCCESS: DataAPIClient initialized successfully!")

        print("\nAttempting to connect to the database...")
        db = client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)
        print("✅ SUCCESS: Connected to the database!")
        
        # Optional: Coba list collections
        # print("\nAttempting to list collections...")
        # collections = db.list_collection_names()
        # print(f"✅ SUCCESS: Found collections: {collections}")

    except Exception as e:
        print(f"\n❌ FAILED to connect to Astra DB.")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Details: {e}")
        print("\n   This is likely the root cause of the backend server crash.")
        print("   Please check if your Astra DB credentials in the .env file are correct.")

print("\n--- Test Finished ---")
