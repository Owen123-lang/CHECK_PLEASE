import React from 'react';
import { Search, History, User } from 'lucide-react';
import Link from 'next/link';

export default function Header() {
  return (
    <header className="flex justify-between items-center px-4 sm:px-6 lg:px-8 py-4 border-b-2 border-[#2a2a2a] bg-brand-dark/95 backdrop-blur-sm z-50">
      <Link href="/" className="flex items-center space-x-3 transition-transform hover:scale-105">
        {/* Logo */}
        <img 
          src="/CheckPlease.svg" 
          alt="Check Please Logo" 
          className="h-[35px] sm:h-[40px] w-auto"
        />
      </Link>
      <nav className="flex items-center space-x-4 lg:space-x-6">
        <a href="#" className="text-gray-400 hover:text-brand-yellow transition-all duration-300 flex items-center space-x-1 text-[14px] lg:text-[16px] font-medium">
          <History size={18} /> <span className="hidden sm:inline">History</span>
        </a>
        <a href="#" className="text-gray-400 hover:text-brand-yellow transition-all duration-300 flex items-center space-x-1 text-[14px] lg:text-[16px] font-medium">
          <Search size={18} /> <span className="hidden sm:inline">Search</span>
        </a>
        <Link 
          href="/login"
          className="bg-brand-yellow text-[#1A1E21] font-bold py-2 px-4 lg:px-6 rounded-lg hover:bg-brand-yellow-dark hover:shadow-lg hover:shadow-brand-yellow/50 transition-all duration-300 flex items-center space-x-2 text-[14px] lg:text-[16px]"
        >
          <User size={18} /> <span>Login</span>
        </Link>
      </nav>
    </header>
  );
}
