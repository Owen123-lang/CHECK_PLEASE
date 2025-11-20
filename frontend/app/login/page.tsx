'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { API_ENDPOINTS } from '@/lib/api';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();

  // Redirect if already logged in
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/chat');
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(API_ENDPOINTS.LOGIN, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.message || 'Invalid email or password');
      }

      // Backend returns data in "payload" property
      const token = data.payload?.token;
      const user = data.payload?.user;

      if (!token || !user) {
        console.error('Login response:', data);
        throw new Error('Invalid response format from server');
      }

      // Use auth context to set authentication
      login(token, user);
      
      // Redirect to chat page on success
      router.push('/chat');
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Invalid email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#1A1E21] flex flex-col">
      {/* Header */}
      <header className="border-b border-[#232B2F]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 lg:py-5">
          <Link href="/" className="inline-block">
            <img 
              src="/CheckPlease.svg" 
              alt="Check Please" 
              className="h-[35px] sm:h-[40px] lg:h-[55px] hover:opacity-80 transition-opacity"
            />
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div className="w-full max-w-md">
          {/* Login Card */}
          <div className="bg-[#232B2F] rounded-2xl shadow-2xl p-6 lg:p-8 border border-[#2A3339]">
            <div className="text-center mb-6 lg:mb-8">
              <h1 className="text-2xl lg:text-3xl font-bold text-white mb-2">
                Welcome Back
              </h1>
              <p className="text-sm lg:text-base text-gray-400">
                Sign in to your account to continue
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-4 p-3 bg-[#FF0000]/10 border border-[#FF0000]/30 rounded-lg">
                <p className="text-sm text-[#FF0000]">{error}</p>
              </div>
            )}

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-4 lg:space-y-5">
              {/* Email Field */}
              <div>
                <label 
                  htmlFor="email" 
                  className="block text-sm font-medium text-gray-300 mb-2"
                >
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-[#1A1E21] border-2 border-[#2A3339] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#FFFF00] transition-colors"
                  placeholder="you@example.com"
                />
              </div>

              {/* Password Field */}
              <div>
                <label 
                  htmlFor="password" 
                  className="block text-sm font-medium text-gray-300 mb-2"
                >
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full px-4 py-3 bg-[#1A1E21] border-2 border-[#2A3339] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#FFFF00] transition-colors pr-12"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center text-gray-400 cursor-pointer hover:text-white transition-colors">
                  <input
                    type="checkbox"
                    className="mr-2 w-4 h-4 rounded border-[#2A3339] bg-[#1A1E21] text-[#FFFF00] focus:ring-[#FFFF00] focus:ring-offset-0"
                  />
                  Remember me
                </label>
                <Link 
                  href="/forgot-password" 
                  className="text-[#FFFF00] hover:text-[#FFD700] transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full px-6 py-3 lg:py-4 bg-[#FF0000] hover:bg-[#D70000] text-white font-semibold rounded-lg transition-all duration-300 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>

            {/* Sign Up Link */}
            <p className="mt-6 lg:mt-8 text-center text-sm text-gray-400">
              Don't have an account?{' '}
              <Link 
                href="/signup" 
                className="text-[#FFFF00] hover:text-[#FFD700] font-semibold transition-colors"
              >
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#232B2F] py-4 lg:py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © 2025 Check Please. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
