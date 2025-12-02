# UUID Migration Fix - Notebook ID Type Mismatch

## Problem
The production database uses **UUID** for notebook IDs, but the frontend code had legacy **INTEGER** validation and type definitions, causing 404 errors when creating or accessing notebooks.

### Error Messages
```
Error executing query error: invalid input syntax for type uuid: "9698"
Error executing query error: invalid input syntax for type uuid: "30"
GET /api/notebooks/9698 404 (Not Found)
```

## Root Cause
1. **Database Schema**: Uses UUID for `notebook.id`
2. **Frontend Code**: Still had INTEGER type definitions and parsing logic from old implementation
3. **Type Mismatch**: Frontend sent numeric IDs to backend expecting UUIDs

## Files Fixed

### 1. `frontend/app/chat/page.tsx`
**Problem**: Converted notebook ID to integer before API calls
```typescript
// ❌ OLD CODE (Lines 76-84)
const numericId = parseInt(notebookId, 10);
if (isNaN(numericId) || numericId <= 0) {
  console.error('Invalid notebook ID:', notebookId);
  return;
}
const response = await fetch(API_ENDPOINTS.NOTEBOOK(numericId), ...);
```

**Solution**: Treat notebook ID as string (UUID)
```typescript
// ✅ NEW CODE
// notebookId is now UUID string, no need to parse
const response = await fetch(API_ENDPOINTS.NOTEBOOK(notebookId), ...);
```

**Interface Change**:
```typescript
// Changed from:
interface PreviousChat {
  notebookId: number;  // ❌
}

// To:
interface PreviousChat {
  notebookId: string;  // ✅ UUID
}
```

### 2. `frontend/components/chat/ChatPanel.tsx`
Updated `PreviousChat` interface:
```typescript
interface PreviousChat {
  id: number;
  notebookId: string;  // Changed from number to string (UUID)
  sender: string;
  body: string;
  created_at: string;
}
```

### 3. `frontend/components/chat/SourcePanel.tsx`
Updated `PreviousChat` interface to match:
```typescript
interface PreviousChat {
  id: number;
  notebookId: string;  // Changed from number to string (UUID)
  sender: string;
  body: string;
  created_at: string;
}
```

## Backend Verification
Backend code was already correct - no changes needed:

### `backend-db/src/repositories/notebook.repository.js`
```javascript
// Already using UUID properly
exports.createNotebook = async (userId, title) => {
  const res = await db.query(
    `INSERT INTO notebook (user_id, title)
     VALUES ($1, $2)
     RETURNING *`,  // Returns UUID automatically
    [userId, title]
  );
  return res.rows[0];
};
```

### Database Schema
```sql
CREATE TABLE notebook (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- UUID type
    user_id INTEGER REFERENCES "user"(id),
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing Steps

### 1. Create New Notebook
```
1. Go to /notebooks page
2. Click "New Notebook" button
3. Enter title and create
4. Should receive UUID (e.g., "30e5febe-d9cb-4046-99e9-2e66b7c46df3")
5. No more "invalid input syntax for type uuid" errors
```

### 2. Access Existing Notebook
```
1. Click on any notebook card
2. Should navigate to /chat?notebook=<UUID>
3. Chat page should load without 404 errors
4. Previous chats should load correctly
```

### 3. API Calls to Verify
```bash
# Get notebook by UUID (should work)
curl https://checkplease-backend-db.onrender.com/api/notebooks/30e5febe-d9cb-4046-99e9-2e66b7c46df3

# Get notebook by old integer ID (should 404)
curl https://checkplease-backend-db.onrender.com/api/notebooks/30
# Response: {"success":false,"statusCode":404,"message":"Notebook not found"}
```

## Migration Notes

### For Existing Users
- All old notebook IDs (integers) are now invalid
- Users need to create new notebooks
- Old chat history with integer IDs cannot be accessed
- Database can be cleaned of orphaned data if needed

### For New Deployments
- No action required
- System will work correctly from the start

## Related Fixes
This fix is part of the larger UUID migration that also addressed:
1. CV Export URL configuration (see `CV_EXPORT_FIX.md`)
2. Production environment variables
3. API endpoint centralization in `frontend/lib/api.ts`

## Summary
**Before**: Frontend treated notebook IDs as integers, causing UUID parsing errors in PostgreSQL
**After**: Frontend correctly treats notebook IDs as UUID strings throughout the application
**Result**: Notebook creation and access now works properly in production