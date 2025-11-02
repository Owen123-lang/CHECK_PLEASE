"use client";
import React, { useState } from 'react';
import { Download, Mail, History, BookOpen, Loader2 } from 'lucide-react'; // Ikon

export default function StudioPanel() {
  const [isExporting, setIsExporting] = useState(false);

  const handleExportPDF = async () => {
    // Untuk saat ini, kita akan mengirim konten dari chat terakhir
    // atau placeholder jika chat kosong.
    // Nanti, ini bisa mengambil hasil "profil" yang sudah diformat dari AI.
    const currentChatContent = document.querySelector('.custom-scrollbar')?.textContent || "No chat content available for export.";
    const profileData = `Generated Report from Check Please:\n\n${currentChatContent}`;
    
    setIsExporting(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/generate-pdf", { // <--- Pastikan ini sesuai
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile_data: profileData }),
      });

      if (!response.ok) {
        throw new Error(`PDF generation failed: ${response.status} ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "CheckPlease_Profile.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      alert("PDF exported successfully!");

    } catch (error: any) {
      console.error("Error exporting PDF:", error);
      alert(`Failed to export PDF: ${error.message || error}`);
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
          className="w-full bg-brand-red text-white font-bold py-3 rounded-lg hover:bg-brand-red-dark transition-colors shadow-md flex items-center justify-center space-x-2 disabled:opacity-50"
          disabled={isExporting}
        >
          {isExporting ? (
            <>
              <Loader2 size={18} className="animate-spin" /> <span>Exporting...</span>
            </>
          ) : (
            <>
              <Download size={18} /> <span>Export Profile to PDF</span>
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
        {/* Updated Search History Placeholders */}
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
