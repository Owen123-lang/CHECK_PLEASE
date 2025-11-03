"use client";
import React, { useState } from 'react';
import { Download, Mail, History, BookOpen, Loader2, FileText } from 'lucide-react';

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
      
      const response = await fetch("http://127.0.0.1:8000/api/generate-cv", {
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
    <aside className="w-1/5 bg-brand-container p-6 overflow-y-auto border-l border-brand-border hidden lg:block">
      <h2 className="text-lg font-bold text-brand-yellow mb-4">Studio</h2>
      
      <div className="space-y-4">
        <button 
          onClick={handleExportPDF}
          className="w-full bg-brand-red text-white font-bold py-3 rounded-lg hover:bg-brand-red-dark transition-colors shadow-md flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isExporting}
          title="Generate professional CV PDF for the professor discussed in chat"
        >
          {isExporting ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              <span>Generating CV...</span>
            </>
          ) : (
            <>
              <FileText size={18} />
              <span>Export Profile to PDF</span>
            </>
          )}
        </button>
        
        <button className="w-full bg-gray-700 text-white font-semibold py-3 rounded-lg hover:bg-gray-600 transition-colors shadow-sm flex items-center justify-center space-x-2">
          <Mail size={18} /> <span>Draft Email to Expert</span>
        </button>
      </div>

      <hr className="border-brand-border my-6" />

      <h3 className="text-md font-bold text-brand-yellow mb-3 flex items-center space-x-2">
        <History size={18} /> <span>Search History</span>
      </h3>
      <div className="space-y-2 text-sm">
        <div className="p-3 bg-gray-800 rounded-md border border-brand-border text-gray-300 hover:bg-gray-700 transition-colors cursor-pointer flex items-center space-x-2">
            <BookOpen size={16} className="text-gray-500" />
            <p className="truncate">"Prof. Riri Fitri Sari"</p>
        </div>
        <div className="p-3 bg-gray-800 rounded-md border border-brand-border text-gray-300 hover:bg-gray-700 transition-colors cursor-pointer flex items-center space-x-2">
            <BookOpen size={16} className="text-gray-500" />
            <p className="truncate">"Dr. Muhammad Suryanegara"</p>
        </div>
        <div className="p-3 bg-gray-800 rounded-md border border-brand-border text-gray-300 hover:bg-gray-700 transition-colors cursor-pointer flex items-center space-x-2">
            <BookOpen size={16} className="text-gray-500" />
            <p className="truncate">"DTE UI Professors"</p>
        </div>
      </div>
    </aside>
  );
}
