# Testing Guide for Check Please Application

## 🧪 Overview

This document provides comprehensive testing procedures for the Check Please AI Research Assistant application across all three layers: Frontend, Backend-DB, and Backend-AI.

## 📋 Testing Checklist

### ✅ Backend-AI Tests (Python FastAPI)

#### 1. Health Check
```bash
# Test if backend is running
curl http://localhost:8000/
# Expected: {"status":"Backend is running"}
```

#### 2. Database Connection Test
```bash
# Run connection test script
cd backend
python test_connections.py
# Expected: "✅ All connections successful!"
```

#### 3. Chat Endpoint Test
```bash
# Test basic chat functionality
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is machine learning?",
    "urls": []
  }'
# Expected: JSON response with AI-generated answer
```

#### 4. CV Generation Test
```bash
# Test CV generation
curl -X POST http://localhost:8000/api/generate-cv \
  -H "Content-Type: application/json" \
  -d '{
    "professor_name": "Prof. Dr. Riri Fitri Sari"
  }' \
  --output test_cv.pdf
# Expected: PDF file downloaded as test_cv.pdf
```

---

### ✅ Backend-DB Tests (Node.js Express)

#### 1. Health Check
```bash
# Test if backend-db is running
curl http://localhost:4000/
# Expected: Server status response
```

#### 2. User Registration Test
```bash
# Test user signup
curl -X POST http://localhost:4000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
# Expected: {"success": true, "data": {...}}
```

#### 3. User Login Test
```bash
# Test user login
curl -X POST http://localhost:4000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
# Expected: {"success": true, "data": {"token": "...", "user": {...}}}
```

#### 4. Notebooks API Test (Requires Authentication)
```bash
# Get all notebooks for user
curl http://localhost:4000/api/notebooks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
# Expected: {"success": true, "data": [...]}
```

#### 5. Chat History Test (Requires Authentication)
```bash
# Get chat history for a notebook
curl http://localhost:4000/api/chat/notebook/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
# Expected: {"success": true, "data": [...]}
```

---

### ✅ Frontend Tests (Next.js)

#### 1. Landing Page Test
- Open: `http://localhost:3001/`
- Expected: Hero section with "Check Please" branding
- Check: Navigation links work (Login, Sign Up)

#### 2. Authentication Flow Test
**Sign Up:**
- Navigate to: `http://localhost:3001/signup`
- Fill form: username, email, password
- Submit
- Expected: Redirect to dashboard

**Login:**
- Navigate to: `http://localhost:3001/login`
- Fill form: email, password
- Submit
- Expected: Redirect to dashboard with JWT token stored

#### 3. Dashboard Test
- Navigate to: `http://localhost:3001/dashboard`
- Expected: List of notebooks (empty or with data)
- Test: Create new notebook button
- Test: Edit/Delete notebook functionality

#### 4. Chat Interface Test
- Navigate to: `http://localhost:3001/chat`
- Test: Send message without URLs
- Test: Send message with URLs
- Test: View sources panel
- Test: View studio panel
- Expected: AI responses appear after ~30-60 seconds

---

## 🔐 Production Deployment Tests

### Frontend (Vercel)
```bash
# Test production frontend
curl https://check-please-gray.vercel.app/
# Expected: Landing page HTML

# Test API connectivity
# Open browser console at https://check-please-gray.vercel.app/login
# Check if NEXT_PUBLIC_API_URL is correctly set
```

### Backend-DB (Render)
```bash
# Test production backend-db
curl https://checkplease-backend-db.onrender.com/
# Expected: Server status response

# Test database connection (should not crash)
# Monitor logs at Render dashboard
```

### Backend-AI (Render)
```bash
# Test production backend-ai
curl https://checkplease-backend-ai.onrender.com/
# Expected: {"status":"Backend is running"}

# Test chat endpoint
curl -X POST https://checkplease-backend-ai.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "urls": []}'
# Expected: JSON response (may take 30-60 seconds)
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Connection Refused
**Symptom:** `ERR_CONNECTION_REFUSED`
**Solution:** 
- Check if server is running
- Verify port numbers (3001, 4000, 8000)
- Check firewall settings

### Issue 2: CORS Error
**Symptom:** `CORS policy: No 'Access-Control-Allow-Origin'`
**Solution:**
- Verify CORS settings in backend
- Check if frontend URL is in allowed origins
- Clear browser cache

### Issue 3: Database Connection Error
**Symptom:** `Connection terminated unexpectedly`
**Solution:**
- Check PostgreSQL connection string
- Verify connection pooling settings (already fixed)
- Check Neon database status

### Issue 4: JWT Token Invalid
**Symptom:** `401 Unauthorized`
**Solution:**
- Re-login to get new token
- Check token expiration
- Verify JWT_SECRET matches between services

### Issue 5: AI Response Timeout
**Symptom:** Request takes >60 seconds
**Solution:**
- Normal for complex queries
- Check Gemini API key validity
- Verify Astra DB connection
- Check internet connectivity

---

## 📊 Performance Benchmarks

### Expected Response Times

| Endpoint | Local | Production |
|----------|-------|------------|
| Health Check | <100ms | <500ms |
| User Login | <500ms | <1s |
| Chat (Simple) | 5-15s | 10-30s |
| Chat (Complex) | 30-60s | 45-90s |
| CV Generation | 20-40s | 30-60s |
| Notebook CRUD | <500ms | <1s |

---

## 🔍 Integration Tests

### End-to-End Test Scenario

1. **User Registration & Login**
   ```
   Register → Login → Store JWT → Verify Dashboard Access
   ```

2. **Create Notebook & Chat**
   ```
   Create Notebook → Open Chat → Send Message → Verify AI Response → Save to Notebook
   ```

3. **CV Generation Flow**
   ```
   Chat: "Generate CV for Prof. X" → AI Collects Data → CV Downloaded → Verify PDF
   ```

4. **Multi-URL Research Flow**
   ```
   Add 3 URLs → Ask Question → AI Scrapes All URLs → Synthesized Answer
   ```

---

## 🛠️ Automated Testing Scripts

### Backend Connection Test
Located at: `backend/test_connections.py`
```bash
cd backend
python test_connections.py
```

### Manual Test Suite
Create a test script to automate all curl tests above.

---

## 📈 Monitoring & Logging

### Local Development
- Backend logs: Check terminal running `uvicorn`
- Frontend logs: Check browser console
- Database logs: Check Neon dashboard

### Production
- Frontend: Vercel deployment logs
- Backend-DB: Render logs dashboard
- Backend-AI: Render logs dashboard
- Database: Neon dashboard metrics

---

## ✅ Test Coverage Goals

- [ ] Unit tests for critical functions
- [x] Integration tests for API endpoints
- [x] End-to-end user flow tests
- [x] Database connection stability tests
- [x] Authentication flow tests
- [x] Error handling tests
- [ ] Performance/load tests
- [ ] Security penetration tests

---

## 📝 Test Results Template

```markdown
### Test Run: [Date]
**Environment:** [Local/Production]
**Tester:** [Name]

| Test Case | Status | Notes |
|-----------|--------|-------|
| Backend Health Check | ✅ | Response time: 50ms |
| User Login | ✅ | JWT token generated |
| Chat Endpoint | ❌ | Timeout after 120s |
| CV Generation | ✅ | PDF size: 245KB |
| Database Connection | ✅ | No crashes in 1 hour |

**Issues Found:**
1. Chat timeout on complex queries - need optimization
2. ...

**Action Items:**
1. Increase timeout to 180s
2. ...
```

---

## 🚀 Quick Test Commands

### Test Everything Locally
```bash
# Terminal 1: Backend-DB
cd backend-db
npm start

# Terminal 2: Backend-AI
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 3: Frontend
cd frontend
npm run dev

# Terminal 4: Run tests
curl http://localhost:4000/ && \
curl http://localhost:8000/ && \
curl http://localhost:3001/
```

### Test Production
```bash
curl https://check-please-gray.vercel.app/ && \
curl https://checkplease-backend-db.onrender.com/ && \
curl https://checkplease-backend-ai.onrender.com/
```

---

**Last Updated:** 2024-11-29  
**Version:** 1.0.0