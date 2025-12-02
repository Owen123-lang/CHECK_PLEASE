# Fix untuk CV Export Error

## Problem
Error: `127.0.0.1:8000/api/generate-cv Failed to load resource: net::ERR_CONNECTION_REFUSED`

Frontend mencoba mengakses localhost padahal harusnya menggunakan production URL untuk AI backend.

## Root Cause
Environment variable `NEXT_PUBLIC_AI_API_URL` tidak diset di Vercel, sehingga fallback ke localhost.

## Changes Made

### 1. Updated `frontend/lib/api.ts`
Added CV generation endpoint:
```typescript
AI_GENERATE_CV: `${AI_API_BASE_URL}/api/generate-cv`,
```

### 2. Updated `frontend/components/chat/StudioPanel.tsx`
- Added import: `import { API_ENDPOINTS } from '@/lib/api';`
- Replaced hardcoded URL with: `API_ENDPOINTS.AI_GENERATE_CV`
- Removed manual URL construction

## Solution Steps

### Step 1: Add Environment Variable to Vercel

1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Select your project: `checkplease-frontend`
3. Go to **Settings** → **Environment Variables**
4. Add new variable:
   - **Name**: `NEXT_PUBLIC_AI_API_URL`
   - **Value**: `https://checkplease-backend-ai.onrender.com` (your AI backend URL)
   - **Environment**: All (Production, Preview, Development)
5. Click **Save**

### Step 2: Redeploy Frontend

After adding the environment variable, you need to trigger a new deployment:

**Option A: Via Git Push**
```bash
cd frontend
git add .
git commit -m "Fix CV export to use production AI backend URL"
git push origin main
```

**Option B: Via Vercel Dashboard**
1. Go to **Deployments** tab
2. Click **...** on latest deployment
3. Select **Redeploy**
4. Check "Use existing Build Cache" (optional)
5. Click **Redeploy**

### Step 3: Verify the Fix

After redeployment:
1. Open browser DevTools (F12)
2. Go to **Console** tab
3. Navigate to chat page
4. Click "Export Profile to PDF" button
5. Check console logs - should see:
   ```
   [CV Export] Calling endpoint: https://checkplease-backend-ai.onrender.com/api/generate-cv
   ```
   (NOT `http://127.0.0.1:8000/api/generate-cv`)

## Technical Details

### Environment Variable Structure
```typescript
// frontend/lib/api.ts
export const AI_API_BASE_URL = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8000';
```

- In **production**: Uses `NEXT_PUBLIC_AI_API_URL` from Vercel
- In **development**: Falls back to `localhost:8000`

### Why NEXT_PUBLIC_ Prefix?
Next.js only exposes environment variables with `NEXT_PUBLIC_` prefix to the browser. Variables without this prefix are server-side only.

## Testing Checklist

- [ ] Environment variable added to Vercel
- [ ] Frontend redeployed
- [ ] Chat page loads without errors
- [ ] Console shows production AI backend URL
- [ ] CV export button works
- [ ] PDF downloads successfully
- [ ] No localhost URLs in production logs

## Related Files
- `frontend/lib/api.ts` - API endpoint definitions
- `frontend/components/chat/StudioPanel.tsx` - CV export functionality
- `backend/main.py` - AI backend with `/api/generate-cv` endpoint

## Backend AI Endpoints
Production URL: `https://checkplease-backend-ai.onrender.com`

Available endpoints:
- `POST /api/chat` - Chat with AI agent
- `POST /api/generate-cv` - Generate professor CV PDF

## Notes
- The AI backend must be running and accessible
- PDF generation requires the professor data to be available in Astra DB
- Session ID is optional but helps with context retention