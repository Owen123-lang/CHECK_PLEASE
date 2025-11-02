from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for this test
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Minimal Test Server is running"}

@app.post("/api/test")
async def handle_test():
    print("✅ Request received at /api/test endpoint!")
    return {"response": "Connection successful! The problem is in the main backend app."}
