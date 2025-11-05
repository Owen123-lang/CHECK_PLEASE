"use client";

import { FileText, Plus, Upload, X, CheckCircle, Loader2 } from 'lucide-react';
import { useState, useRef } from 'react';

interface SourcePanelProps {
  sessionId?: string | null;
  onPdfUploaded?: (filename: string) => void;
}

export default function SourcePanel({ sessionId, onPdfUploaded }: SourcePanelProps) {
  const [uploadedPdfs, setUploadedPdfs] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    <aside className="w-1/5 bg-brand-container p-4 overflow-y-auto border-r border-brand-border hidden md:block">
      <h2 className="text-lg font-bold text-brand-yellow mb-4">Sources</h2>
      
      {/* Upload Status Messages */}
      {uploadSuccess && (
        <div className="mb-3 p-3 bg-green-900 text-green-300 rounded-lg text-sm flex items-start space-x-2">
          <CheckCircle size={16} className="mt-0.5 flex-shrink-0" />
          <span>{uploadSuccess}</span>
        </div>
      )}
      
      {uploadError && (
        <div className="mb-3 p-3 bg-red-900 text-red-300 rounded-lg text-sm flex items-start space-x-2">
          <X size={16} className="mt-0.5 flex-shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      <div className="space-y-3">
        {uploadedPdfs.length === 0 ? (
          <p className="text-gray-500 text-sm">
            Upload your PDF documents here. The AI will be able to answer questions based on your uploaded files.
          </p>
        ) : (
          <>
            <p className="text-gray-400 text-xs mb-2">📄 Uploaded PDFs:</p>
            {uploadedPdfs.map((filename, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-800 rounded-lg border border-brand-border hover:bg-gray-700 transition-colors group">
                <div className="flex items-center space-x-2 flex-1 min-w-0">
                  <FileText size={18} className="text-brand-yellow flex-shrink-0" />
                  <p className="font-semibold text-gray-200 truncate text-sm">{filename}</p>
                </div>
                <button
                  onClick={() => handleRemovePdf(filename)}
                  className="ml-2 text-red-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Remove"
                >
                  <X size={16} />
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
        className="w-full mt-6 flex items-center justify-center space-x-2 bg-brand-yellow text-black font-bold py-2 px-4 rounded-lg hover:bg-brand-yellow-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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

      <p className="text-xs text-gray-500 mt-2 text-center">
        Max 10MB • PDF only
      </p>
    </aside>
  );
}
