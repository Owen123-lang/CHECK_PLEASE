import React from 'react';

export default function LandingHeader() {
  return (
    <header className="bg-black border-b border-gray-800 flex justify-between items-center p-4">
      <div className="flex items-center">
        <span className="text-yellow-400 font-bold text-xl tracking-wide">
          CHECK PLEASE
        </span>
      </div>
      <nav className="flex items-center">
        {/* Hamburger Menu Placeholder */}
        <div className="w-8 h-8 border border-white rounded"></div>
      </nav>
    </header>
  );
}
