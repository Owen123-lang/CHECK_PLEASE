import React from 'react';
import { Search, History, User } from 'lucide-react'; // Ikon dari lucide-react

export default function Header() {
  return (
    <header className="flex justify-between items-center p-4 border-b border-brand-border bg-brand-dark z-50">
      <div className="flex items-center space-x-3">
        {/* Logo Placeholder */}
        <div className="w-8 h-8 bg-brand-yellow rounded-full flex items-center justify-center">
          <span className="text-black font-bold text-sm">CP</span>
        </div> 
        <span className="text-xl font-bold text-brand-yellow tracking-wide">
          CHECK PLEASE
        </span>
      </div>
      <nav className="flex items-center space-x-6">
        <a href="#" className="text-gray-400 hover:text-brand-yellow transition-colors flex items-center space-x-1">
          <History size={18} /> <span>History</span>
        </a>
        <a href="#" className="text-gray-400 hover:text-brand-yellow transition-colors flex items-center space-x-1">
          <Search size={18} /> <span>Search</span>
        </a>
        <button className="bg-brand-yellow text-black font-bold py-2 px-4 rounded-lg hover:bg-brand-yellow-dark transition-colors flex items-center space-x-2">
          <User size={18} /> <span>Login</span>
        </button>
      </nav>
    </header>
  );
}
