// Authentication utility functions
export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  payload?: {
    token: string;
    user: User;
  };
}

// Get token from localStorage
export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
};

// Get user from localStorage
export const getUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
};

// Set authentication data
export const setAuth = (token: string, user: User): void => {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
};

// Clear authentication data
export const clearAuth = (): void => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return !!getToken();
};

// Decode JWT token to check expiration
export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
};

// Check if current token is valid
export const isTokenValid = (): boolean => {
  const token = getToken();
  if (!token) return false;
  return !isTokenExpired(token);
};

// API call with authentication
export const authenticatedFetch = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getToken();
  
  if (!token) {
    throw new Error('No authentication token');
  }

  const headers: HeadersInit = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
  };

  if (options.body && typeof options.body === 'object') {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // If token is expired or invalid, clear auth and redirect
  if (response.status === 401) {
    clearAuth();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }

  return response;
};