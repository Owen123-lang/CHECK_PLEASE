"use client";

import { FileText, Plus, Upload, X, CheckCircle, Loader2, Download, FileUp, Trash2, MessageCircle } from 'lucide-react';
import { useState, useRef } from 'react';

interface PreviousChat {
  id: number;
  notebookId: string;  // Changed to string (UUID)
  sender: string;
  body: string;
  created_at: string;
}

interface SourcePanelProps {
  sessionId?: string | null;
  lastMessage?: string | null;
  onPdfUploaded?: (filename: string) => void;
  notebookId?: string;
  previousChats?: PreviousChat[];
}

export default function SourcePanel({ 
  sessionId, 
  lastMessage, 
  onPdfUploaded, 
  notebookId, 
  previousChats = [] 
}: SourcePanelProps) {
  const [uploadedPdfs, setUploadedPdfs] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.pdf')) {
      setUploadError('Only PDF files are allowed');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File size must be less than 10MB');
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (sessionId) {
        formData.append('session_id', sessionId);
      }

      const response = await fetch('http://127.0.0.1:8000/api/upload-pdf', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      const data = await response.json();
      
      // Add to uploaded list
      setUploadedPdfs(prev => [...prev, data.filename]);
      setUploadSuccess(`✓ ${data.filename} uploaded! (${data.pages} pages, ${data.chunks_stored} chunks)`);
      
      // Notify parent component
      onPdfUploaded?.(data.filename);

      // Clear success message after 5 seconds
      setTimeout(() => setUploadSuccess(null), 5000);

    } catch (error: any) {
      console.error('PDF upload error:', error);
      setUploadError(error.message || 'Failed to upload PDF');
    } finally {
      setIsUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleAddSourceClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemovePdf = (filename: string) => {
    setUploadedPdfs(prev => prev.filter(pdf => pdf !== filename));
  };

  return (
    <aside className="w-64 lg:w-72 bg-[#15191C] p-4 lg:p-6 overflow-y-auto border-r-2 border-brand-border hidden md:block custom-scrollbar">
      <h2 className="text-lg lg:text-xl font-bold text-brand-yellow mb-4 lg:mb-6 flex items-center gap-2">
        <FileText size={20} />
        Sources
      </h2>
      
      {/* Upload Status Messages */}
      {uploadSuccess && (
        <div className="mb-4 p-3 lg:p-4 bg-green-900/30 border border-green-700 text-green-300 rounded-xl text-sm flex items-start space-x-2 animate-in fade-in slide-in-from-top duration-300">
          <CheckCircle size={18} className="mt-0.5 flex-shrink-0" />
          <span>{uploadSuccess}</span>
        </div>
      )}
      
      {uploadError && (
        <div className="mb-4 p-3 lg:p-4 bg-red-900/30 border border-red-700 text-red-300 rounded-xl text-sm flex items-start space-x-2 animate-in fade-in slide-in-from-top duration-300">
          <X size={18} className="mt-0.5 flex-shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      <div className="space-y-3">
        {uploadedPdfs.length === 0 ? (
          <div className="p-4 bg-brand-dark rounded-xl border border-brand-border">
            <p className="text-gray-400 text-sm leading-relaxed">
              Upload your PDF documents here. The AI will be able to answer questions based on your uploaded files.
            </p>
          </div>
        ) : (
          <>
            <p className="text-gray-400 text-xs mb-3 font-medium">📄 Uploaded PDFs:</p>
            {uploadedPdfs.map((filename, index) => (
              <div key={index} className="flex items-center justify-between p-3 lg:p-4 bg-brand-dark rounded-xl border border-brand-border hover:border-brand-yellow/50 transition-all duration-300 group hover:scale-105">
                <div className="flex items-center space-x-2 flex-1 min-w-0">
                  <FileText size={18} className="text-brand-yellow flex-shrink-0" />
                  <p className="font-semibold text-gray-200 truncate text-sm">{filename}</p>
                </div>
                <button
                  onClick={() => handleRemovePdf(filename)}
                  className="ml-2 text-red-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all duration-300"
                  title="Remove"
                >
                  <X size={18} />
                </button>
              </div>
            ))}
          </>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Add New Source Button */}
      <button
        onClick={handleAddSourceClick}
        disabled={isUploading}
        className="w-full mt-6 flex items-center justify-center space-x-2 bg-brand-yellow text-[#1A1E21] font-bold py-3 px-4 rounded-xl hover:bg-brand-yellow-dark hover:shadow-lg hover:shadow-brand-yellow/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isUploading ? (
          <>
            <Loader2 size={18} className="animate-spin" />
            <span>Uploading...</span>
          </>
        ) : (
          <>
            <Upload size={18} />
            <span>Upload PDF</span>
          </>
        )}
      </button>

      <p className="text-xs text-gray-500 mt-3 text-center font-medium">
        Max 10MB • PDF only
      </p>

      {/* Studio Section */}
      <hr className="border-brand-border my-6 lg:my-8" />
      
      <h2 className="text-lg lg:text-xl font-bold text-brand-yellow mb-4 flex items-center gap-2">
        <FileText size={20} />
        Studio
      </h2>
      
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
    </aside>
  );
}
