"use client";
import React, { useState } from 'react';
import { Download, FileText } from 'lucide-react';
import CVGeneratorModal from './CVGeneratorModal';

interface StudioPanelProps {
  sessionId?: string | null;
  lastMessage?: string | null;
}

export default function StudioPanel({ sessionId, lastMessage }: StudioPanelProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <aside className="w-64 lg:w-72 bg-[#15191C] p-4 lg:p-6 border-l-2 border-brand-border hidden lg:block">
      <h2 className="text-lg lg:text-xl font-bold text-brand-yellow mb-4 lg:mb-6 flex items-center gap-2">
        <FileText size={20} />
        Studio
      </h2>
      
      <div className="space-y-3 lg:space-y-4">
        <button
          onClick={() => setIsModalOpen(true)}
          className="w-full bg-brand-red text-white font-bold py-3 lg:py-4 rounded-xl hover:bg-brand-red-dark hover:shadow-lg hover:shadow-brand-red/50 transition-all duration-300 shadow-md flex items-center justify-center space-x-2 transform hover:scale-105"
          title="Generate professional CV PDF for any professor or lecturer"
        >
          <Download size={18} />
          <span className="text-sm lg:text-base">Export Profile to PDF</span>
        </button>
      </div>

      {/* CV Generator Modal */}
      <CVGeneratorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        sessionId={sessionId}
      />
    </aside>
  );
}
