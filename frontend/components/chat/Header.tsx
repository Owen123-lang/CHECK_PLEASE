'use client';

import React from 'react';
import { User, LogOut } from 'lucide-react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="border-b border-[#2a2a2a] bg-[#1A1E21]/95 backdrop-blur-sm z-50">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-4 lg:py-6">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 transition-transform hover:scale-105">
            <img
              src="/CheckPlease.svg"
              alt="Check Please Logo"
              className="h-[35px] sm:h-[40px] lg:h-[55px] w-auto"
            />
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-4 xl:gap-6">
            {isAuthenticated && (
              <>
                <Link
                  href="/notebooks"
                  className="text-white text-[16px] xl:text-[20px] font-semibold hover:text-[#FFFF00] transition-all duration-300 relative group"
                >
                  Notebooks
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-[#FFFF00] transition-all duration-300 group-hover:w-full" />
                </Link>
                <span className="text-gray-400 text-[16px] xl:text-[20px] hidden md:inline">
                  {user?.name}
                </span>
                <button
                  onClick={logout}
                  className="px-6 xl:px-8 py-2 xl:py-3 bg-[#FF0000] text-white text-[16px] xl:text-[20px] font-semibold rounded-[10px] hover:bg-[#D70000] hover:shadow-lg hover:shadow-[#FF0000]/50 transition-all duration-300 transform hover:scale-105"
                >
                  Logout
                </button>
              </>
            )}
            {!isAuthenticated && (
              <Link
                href="/login"
                className="px-6 xl:px-8 py-2 xl:py-3 bg-[#FFFF00] text-[#1A1E21] text-[16px] xl:text-[20px] font-semibold rounded-[10px] hover:bg-[#FFD700] hover:shadow-lg hover:shadow-[#FFFF00]/50 transition-all duration-300 transform hover:scale-105"
              >
                Login
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
