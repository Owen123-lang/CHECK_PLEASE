# Authentication Implementation Guide

## Overview
This document describes the JWT-based authentication system implemented for the Check Please frontend application.

## Architecture

### Core Components

#### 1. Authentication Utilities (`lib/auth.ts`)
- **Purpose**: Core authentication functions and API helpers
- **Key Functions**:
  - `getToken()`: Retrieves JWT token from localStorage
  - `getUser()`: Retrieves user data from localStorage
  - `setAuth()`: Stores token and user data
  - `clearAuth()`: Removes authentication data
  - `isAuthenticated()`: Checks if user is logged in
  - `isTokenValid()`: Validates JWT token expiration
  - `authenticatedFetch()`: Wrapper for authenticated API calls

#### 2. Authentication Context (`contexts/AuthContext.tsx`)
- **Purpose**: Global authentication state management
- **Provides**:
  - `user`: Current user object
  - `token`: JWT token
  - `isAuthenticated`: Boolean authentication status
  - `isLoading`: Loading state during initialization
  - `login()`: Function to log in user
  - `logout()`: Function to log out user

#### 3. Protected Route Component (`components/auth/ProtectedRoute.tsx`)
- **Purpose**: Wrapper component that requires authentication
- **Behavior**:
  - Redirects to `/login` if user is not authenticated
  - Shows loading spinner while checking auth status
  - Renders children only when authenticated

#### 4. API Configuration (`lib/api.ts`)
- **Purpose**: Centralized API endpoint configuration
- **Features**:
  - Base URL from environment or default
  - Named endpoints for all API routes
  - Type-safe endpoint builders

## Implementation Details

### Session Flow

1. **User Login**:
   ```
   User enters credentials → API call to /api/users/login → 
   Receive JWT token + user data → Store in localStorage → 
   Update AuthContext → Redirect to /chat
   ```

2. **Session Persistence**:
   - On page load, AuthContext checks localStorage for token
   - If valid token exists, user is automatically logged in
   - If token is expired, it's cleared and user redirects to login

3. **Authenticated Requests**:
   ```
   Component calls authenticatedFetch() → 
   Automatically adds Authorization header with Bearer token →
   If 401 response, clears auth and redirects to login
   ```

4. **User Logout**:
   ```
   User clicks logout → clearAuth() removes token/user →
   AuthContext updates state → Redirect to home page
   ```

### Protected Routes

The following pages are protected and require authentication:
- `/chat` - Main chat interface
- `/notebooks` - Notebook management
- `/dashboard` - User dashboard

### Token Management

- **Storage**: JWT tokens are stored in localStorage
- **Expiration**: Tokens expire after 6 hours (configurable in backend)
- **Validation**: Token expiration is checked before use
- **Auto-logout**: Invalid/expired tokens trigger automatic logout

## Security Considerations

1. **Token Storage**: 
   - Tokens are stored in localStorage (client-side)
   - Consider httpOnly cookies for enhanced security in production

2. **Token Transmission**:
   - Tokens are sent via Authorization header as Bearer tokens
   - Always use HTTPS in production

3. **XSS Protection**:
   - Sanitize user inputs
   - Use Content Security Policy headers

4. **CSRF Protection**:
   - Not required for JWT Bearer tokens in headers
   - Required if using cookies

## Usage Examples

### Using Protected Routes
```tsx
import ProtectedRoute from '@/components/auth/ProtectedRoute';

export default function MyPage() {
  return (
    <ProtectedRoute>
      <div>Protected content here</div>
    </ProtectedRoute>
  );
}
```

### Using Auth Context
```tsx
import { useAuth } from '@/contexts/AuthContext';

export default function MyComponent() {
  const { user, isAuthenticated, logout } = useAuth();
  
  if (!isAuthenticated) return null;
  
  return (
    <div>
      <p>Welcome, {user?.name}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Making Authenticated API Calls
```tsx
import { authenticatedFetch } from '@/lib/auth';
import { API_ENDPOINTS } from '@/lib/api';

const fetchData = async () => {
  const response = await authenticatedFetch(API_ENDPOINTS.NOTEBOOKS);
  const data = await response.json();
  return data;
};
```

## Environment Variables

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:4000
```

## Testing the Implementation

1. **Start the backend server**:
   ```bash
   cd backend-db
   npm start
   ```

2. **Start the frontend server**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Flow**:
   - Navigate to `/signup` and create an account
   - Login with the created account
   - Verify redirect to `/chat`
   - Check that user info appears in header
   - Navigate to `/notebooks` (should work)
   - Click logout (should redirect to home)
   - Try accessing `/chat` directly (should redirect to login)

## Backend Requirements

The backend must provide these endpoints:

- `POST /api/users/register` - User registration
- `POST /api/users/login` - User login (returns token + user)
- All protected endpoints must accept `Authorization: Bearer <token>` header
- Return 401 status for invalid/expired tokens

## Future Enhancements

1. **Token Refresh**: Implement refresh token mechanism
2. **Remember Me**: Extended session duration option
3. **Session Timeout**: Automatic logout after inactivity
4. **Multi-factor Authentication**: Add 2FA support
5. **Session Management**: View and revoke active sessions
6. **Password Reset**: Email-based password recovery

## Troubleshooting

### Common Issues

1. **Redirecting to login on refresh**:
   - Check if token is expired
   - Verify token format in localStorage
   - Check backend JWT secret matches

2. **401 Errors on API calls**:
   - Verify token is being sent in header
   - Check token hasn't expired
   - Ensure backend is accepting the token

3. **Login successful but no redirect**:
   - Check browser console for errors
   - Verify router is working correctly
   - Check if response contains expected data structure

## Support

For issues or questions about the authentication system, refer to:
- Backend authentication: `backend-db/src/middleware/auth.middleware.js`
- JWT utilities: `backend-db/src/utils/jwt.util.js`
- User controller: `backend-db/src/controllers/user.controller.js`