'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, getToken, getUser, setAuth, clearAuth, isTokenValid } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on mount
    const initAuth = () => {
      const storedToken = getToken();
      const storedUser = getUser();

      if (storedToken && storedUser && isTokenValid()) {
        setToken(storedToken);
        setUser(storedUser);
      } else if (storedToken) {
        // Token exists but is invalid/expired
        clearAuth();
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = (newToken: string, newUser: User) => {
    setAuth(newToken, newUser);
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    clearAuth();
    setToken(null);
    setUser(null);
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};