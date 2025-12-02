# PDF Search Tool Fix - Error "Invalid response from LLM"

## 🐛 Problem

User mengalami error saat bertanya tentang PDF yang telah diupload:

```
Received None or empty response from LLM call.
Error details: Invalid response from LLM call - None or empty.
```

Agent mengembalikan JSON action dalam Final Answer, bukan menjalankan tool:

```json
{
  "tool_name": "User PDF Search Tool",
  "tool_input": {
    "query": "isi dari pdf CV"
  }
}
```

## 🔍 Root Cause Analysis

### 1. **PDFSearchTool tidak menggunakan session_id**
- Tool memiliki parameter `session_id` tapi tidak digunakan dengan benar
- Session context dari global variable tidak dipanggil
- PDF search gagal menemukan dokumen yang benar

### 2. **Task prompt terlalu kompleks**
- Format output yang terlalu spesifik membingungkan agent
- Agent mencoba menjelaskan apa yang akan dilakukan daripada menjalankannya
- Instruksi "YOU MUST DO THIS" tidak efektif

### 3. **Agent tidak mengeksekusi tool dengan benar**
- LLM mengembalikan JSON format planning daripada actual tool execution
- CrewAI agent stuck dalam "thinking mode" dan tidak action

## ✅ Solutions Applied

### Fix 1: Auto-Import Session Context di PDFSearchTool

**File**: `backend/tools.py` (line 1132-1142)

```python
def _run(self, query: str, session_id: str = None) -> str:
    """Search through uploaded PDF content stored in database with optional session filtering."""
    # Import session context from agent_core
    from agent_core import get_session_context
    
    # If session_id not provided, try to get it from global context
    if not session_id:
        session_id = get_session_context()
        if session_id:
            print(f"[PDF_SEARCH] Using session_id from global context: {session_id}")
    
    # ... rest of the code
```

**Benefit**: Tool sekarang otomatis mengambil session_id dari global context jika tidak diberikan sebagai parameter.

### Fix 2: Simplify PDF Query Task Description

**File**: `backend/agent_core.py` (line 624-636)

**BEFORE** (Too Complex):
```python
task_description = f"""USER QUERY: "{query}"

**MANDATORY ACTION - YOU MUST DO THIS:**

STEP 1: Use the 'User PDF Search Tool' with this exact search query: "{query}"
STEP 2: Read the results from the tool
STEP 3: Summarize the PDF content in Indonesian

**OUTPUT FORMAT (use this exactly):**

# Ringkasan Dokumen PDF
## 📄 Informasi Utama
[Main information from PDF]
...
**CRITICAL:** You CANNOT answer without using the PDF Search Tool first. Execute it NOW."""
```

**AFTER** (Simple & Direct):
```python
task_description = f"""USER QUERY: "{query}"

**YOUR TASK:**
1. Execute the 'User PDF Search Tool' with query: "{query}"
2. Summarize the PDF content found in Indonesian language
3. Format the answer nicely with headers and bullet points

**IMPORTANT RULES:**
- You MUST use the PDF Search Tool to get the content
- DO NOT return JSON - return actual formatted text
- Summarize in Indonesian language
- Keep the answer clear and well-structured

Start by using the PDF Search Tool NOW."""
```

**Benefits**:
- Lebih simpel dan jelas
- Eksplisit menyuruh "DO NOT return JSON"
- Fokus pada action, bukan planning

### Fix 3: Improve Agent Backstory

**File**: `backend/agent_core.py` (line 587-600)

**ADDED**:
```python
"9. **CRITICAL: When user asks about PDF/document they uploaded:**\n"
"   - Use 'User PDF Search Tool' immediately\n"
"   - The tool will automatically use the correct session_id\n"
"   - DO NOT return JSON format - return actual human-readable text\n"
"   - Summarize the PDF content in Indonesian language\n"
```

**Benefit**: Agent tahu secara eksplisit bahwa tool akan handle session_id dan tidak perlu return JSON.

## 🧪 Testing

### Test Case 1: PDF Query dengan Session ID
```
Query: "tolong jelasin kepada saya isi dari pdf CV itu ya"
Session ID: "6915a92e-4d61-4178-b4f1-09694d2f7243"

Expected:
✅ Tool menggunakan session_id dari global context
✅ Agent mengeksekusi tool (bukan return JSON)
✅ Response dalam bahasa Indonesia dengan format yang rapi
```

### Test Case 2: PDF Query tanpa Session ID
```
Query: "apa isi dari dokumen yang saya upload?"
Session ID: None

Expected:
✅ Tool fallback ke semua user PDFs
✅ Masih bisa menemukan dan merangkum PDF
✅ Response jelas tentang sumber data
```

## 📝 Deployment Checklist

- [x] Fix PDFSearchTool session context
- [x] Simplify PDF query task prompt
- [x] Update agent backstory
- [ ] Push ke GitHub
- [ ] Deploy ke Render (restart service)
- [ ] Test di production

## 🎯 Expected Behavior After Fix

1. **User upload PDF** → Stored with session_id
2. **User asks "jelasin isi PDF"** → System detects PDF query
3. **Agent executes PDFSearchTool** → Tool auto-gets session_id
4. **Tool searches database** → Finds PDF chunks with matching session
5. **Agent summarizes** → Returns formatted Indonesian text
6. **User sees answer** → Clear, structured summary

## 🚨 Important Notes

- Session ID harus di-pass dari `main.py` ke `agent_core.py` via `set_session_context(session_id)`
- PDF chunks harus di-store dengan `session_id` field saat upload
- Tool akan fallback ke semua user PDFs jika session_id tidak ditemukan

## 📚 Related Files

- `backend/tools.py` - PDFSearchTool implementation
- `backend/agent_core.py` - Agent configuration & task prompts
- `backend/main.py` - API endpoint yang call agent dengan session_id

## 🔗 References

- CrewAI Documentation: https://docs.crewai.com/
- Astra DB Vector Search: https://docs.datastax.com/en/astra/
- Google Gemini Pro 2.5: https://ai.google.dev/