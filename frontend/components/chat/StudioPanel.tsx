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
    
    // Look for common patterns: Prof., Dr., etc.
    const patterns = [
      /(?:Prof\.?\s*)?(?:Dr\.?\s*)?(?:Ir\.?\s*)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)/,
      /untuk\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)/i,
      /for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)/i,
      /about\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)/i,
    ];
    
    for (const pattern of patterns) {
      const match = content.match(pattern);
      if (match) {
        return match[0].trim();
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
