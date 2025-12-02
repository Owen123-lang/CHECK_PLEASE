"use client";
import React, { useState } from 'react';
import { Download, Loader2, FileText } from 'lucide-react';
import { API_ENDPOINTS } from '@/lib/api';

interface StudioPanelProps {
  sessionId?: string | null;
  lastMessage?: string | null;
}

export default function StudioPanel({ sessionId, lastMessage }: StudioPanelProps) {
  const [isExporting, setIsExporting] = useState(false);

  // Function to extract professor name from chat content
  const extractProfessorName = (content: string): string | null => {
    if (!content) return null;
    
    // Filter out UI text and common words first
    const excludeWords = ['export', 'profile', 'button', 'download', 'pdf', 'generate', 'studio'];
    const lowerContent = content.toLowerCase();
    
    // Skip if content contains UI-related words
    if (excludeWords.some(word => lowerContent.includes(word) && lowerContent.length < 50)) {
      return null;
    }
    
    // Look for academic titles with names (more specific patterns)
    const patterns = [
      // Match "Prof. Dr. FirstName LastName" or similar
      /(Prof\.?\s+)?(?:Dr\.?\s+)?(?:Ir\.?\s+)?(?:Drs\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})(?:\s*,?\s*M\.\w+\.?)?/,
      // Match "about/for Professor Name"
      /(?:about|for|tentang)\s+(Prof\.?\s+)?(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})/i,
      // Match names in quotes
      /"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})"/,
      // Match names after "tell me about" or similar
      /tell\s+me\s+about\s+(Prof\.?\s+)?(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})/i,
    ];
    
    for (const pattern of patterns) {
      const match = content.match(pattern);
      if (match) {
        // Get the full match or the captured group
        const name = match[0].trim();
        
        // Validate: must contain at least 2 words and not be too short
        const words = name.split(/\s+/).filter(w => w.length > 1);
        if (words.length >= 2 && name.length > 8) {
          return name;
        }
      }
    }
    return null;
  };

  const handleExportPDF = async () => {
    // Get all chat content from the page
    const chatArea = document.querySelector('.custom-scrollbar');
    const chatContent = chatArea?.textContent || "";
    
    // Try to extract professor name from last message or full chat
    const professorName = extractProfessorName(lastMessage || chatContent);
    
    if (!professorName) {
      alert('⚠️ Tidak dapat mendeteksi nama profesor.\n\nSilakan tanyakan tentang profesor tertentu terlebih dahulu, misalnya:\n"Tell me about Prof. Dr. Riri Fitri Sari"');
      return;
    }

    setIsExporting(true);
    
    try {
      console.log('[CV Export] Generating CV for:', professorName);
      console.log('[CV Export] Session ID:', sessionId);
      console.log('[CV Export] Calling endpoint:', API_ENDPOINTS.AI_GENERATE_CV);
      
      const response = await fetch(API_ENDPOINTS.AI_GENERATE_CV, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          professor_name: professorName,
          session_id: sessionId || undefined
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Server error: ${response.status}`);
      }

      // Download the PDF
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `CV_${professorName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      
      alert(`✅ CV untuk ${professorName} berhasil didownload!`);

    } catch (error: any) {
      console.error("Error exporting CV:", error);
      alert(`❌ Gagal generate CV: ${error.message}\n\nPastikan backend server berjalan dan nama profesor tersedia.`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <aside className="w-64 lg:w-72 bg-[#15191C] p-4 lg:p-6 border-l-2 border-brand-border hidden lg:block">
      <h2 className="text-lg lg:text-xl font-bold text-brand-yellow mb-4 lg:mb-6 flex items-center gap-2">
        <FileText size={20} />
        Studio
      </h2>
      
      <div className="space-y-3 lg:space-y-4">
        <button 
          onClick={handleExportPDF}
          className="w-full bg-brand-red text-white font-bold py-3 lg:py-4 rounded-xl hover:bg-brand-red-dark hover:shadow-lg hover:shadow-brand-red/50 transition-all duration-300 shadow-md flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105"
          disabled={isExporting}
          title="Generate professional CV PDF for the professor discussed in chat"
        >
          {isExporting ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              <span className="text-sm lg:text-base">Generating CV...</span>
            </>
          ) : (
            <>
              <Download size={18} />
              <span className="text-sm lg:text-base">Export Profile to PDF</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
