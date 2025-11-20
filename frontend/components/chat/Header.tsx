'use client';

import React, { useState, useEffect } from 'react';
import { Search, History, User, LogOut } from 'lucide-react';
import Link from 'next/link';

interface HeaderProps {
  notebookTitle?: string;
}

interface UserData {
  id: string;
  name: string;
  email: string;
  role: string;
}

export default function Header({ notebookTitle }: HeaderProps) {
  const [user, setUser] = useState<UserData | null>(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
  };

  return (
    <header className="flex justify-between items-center px-4 sm:px-6 lg:px-8 py-4 border-b-2 border-[#2a2a2a] bg-brand-dark/95 backdrop-blur-sm z-50">
      <Link href="/" className="flex items-center space-x-3 transition-transform hover:scale-105">
        {/* Logo */}
        <img
          src="/CheckPlease.svg"
          alt="Check Please Logo"
          className="h-[35px] sm:h-[40px] w-auto"
        />
        {notebookTitle && (
          <div className="hidden sm:block">
            <p className="text-xs text-gray-500">Notebook:</p>
            <p className="text-sm font-semibold text-white truncate">{notebookTitle}</p>
          </div>
        )}
      </Link>
      <nav className="flex items-center space-x-4 lg:space-x-6">
        <a
          href="#"
          className="text-gray-400 hover:text-brand-yellow transition-all duration-300 flex items-center space-x-1 text-[14px] lg:text-[16px] font-medium"
        >
          <History size={18} /> <span className="hidden sm:inline">History</span>
        </a>
        <a
          href="#"
          className="text-gray-400 hover:text-brand-yellow transition-all duration-300 flex items-center space-x-1 text-[14px] lg:text-[16px] font-medium"
        >
          <Search size={18} /> <span className="hidden sm:inline">Search</span>
        </a>
        {user ? (
          <div className="flex items-center space-x-3">
            <div className="hidden sm:block text-right">
              <p className="text-sm font-semibold text-white">{user.name}</p>
              <p className="text-xs text-gray-400">{user.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="bg-brand-red text-white font-bold py-2 px-4 lg:px-6 rounded-lg hover:bg-red-700 hover:shadow-lg hover:shadow-brand-red/50 transition-all duration-300 flex items-center space-x-2 text-[14px] lg:text-[16px]"
            >
              <LogOut size={18} /> <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="bg-brand-yellow text-[#1A1E21] font-bold py-2 px-4 lg:px-6 rounded-lg hover:bg-brand-yellow-dark hover:shadow-lg hover:shadow-brand-yellow/50 transition-all duration-300 flex items-center space-x-2 text-[14px] lg:text-[16px]"
          >
            <User size={18} /> <span>Login</span>
          </Link>
        )}
      </nav>
    </header>
  );
}
