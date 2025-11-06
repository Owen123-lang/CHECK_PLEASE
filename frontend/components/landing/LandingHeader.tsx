'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function LandingHeader() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-[#1A1E21]/95 backdrop-blur-sm border-b border-[#2a2a2a]">
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

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-4 xl:gap-6">
            <Link
              href="#features"
              className="text-white text-[16px] xl:text-[20px] font-semibold hover:text-[#FFFF00] transition-all duration-300 relative group"
            >
              Features
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-[#FFFF00] transition-all duration-300 group-hover:w-full" />
            </Link>
            <Link
              href="#about"
              className="text-white text-[16px] xl:text-[20px] font-semibold hover:text-[#FFFF00] transition-all duration-300 relative group"
            >
              About Us
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-[#FFFF00] transition-all duration-300 group-hover:w-full" />
            </Link>
            <Link
              href="/login"
              className="px-6 xl:px-8 py-2 xl:py-3 bg-[#FFFF00] text-[#1A1E21] text-[16px] xl:text-[20px] font-semibold rounded-[10px] hover:bg-[#FFD700] hover:shadow-lg hover:shadow-[#FFFF00]/50 transition-all duration-300 transform hover:scale-105"
            >
              Login
            </Link>
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden text-white p-2 hover:text-[#FFFF00] transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <nav className="lg:hidden mt-4 pb-4 flex flex-col gap-4 animate-in slide-in-from-top duration-300">
            <Link
              href="#features"
              onClick={() => setMobileMenuOpen(false)}
              className="text-white text-[20px] font-semibold hover:text-[#FFFF00] transition-colors py-2 border-b border-[#2a2a2a]"
            >
              Features
            </Link>
            <Link
              href="#about"
              onClick={() => setMobileMenuOpen(false)}
              className="text-white text-[20px] font-semibold hover:text-[#FFFF00] transition-colors py-2 border-b border-[#2a2a2a]"
            >
              About Us
            </Link>
            <Link
              href="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="text-center px-6 py-3 bg-[#FFFF00] text-[#1A1E21] text-[20px] font-semibold rounded-[10px] hover:bg-[#FFD700] transition-colors"
            >
              Login
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
}
