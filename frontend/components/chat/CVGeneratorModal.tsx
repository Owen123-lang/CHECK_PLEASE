"use client";

import { X, Download, Loader2, UserCircle } from 'lucide-react';
import { useState } from 'react';
import { API_ENDPOINTS } from '@/lib/api';

interface CVGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId?: string | null;
}

export default function CVGeneratorModal({ isOpen, onClose, sessionId }: CVGeneratorModalProps) {
  const [professorName, setProfessorName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!professorName.trim()) {
      setError('Silakan masukkan nama profesor/lecturer');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      console.log('[CV Generator] Generating CV for:', professorName);
      console.log('[CV Generator] Session ID:', sessionId);

      const response = await fetch(API_ENDPOINTS.AI_GENERATE_CV, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          professor_name: professorName.trim(),
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
      const a = document.createElement('a');
      a.href = url;
      a.download = `CV_${professorName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();

      // Success - close modal and reset
      alert(`✅ CV untuk ${professorName} berhasil didownload!`);
      setProfessorName('');
      onClose();

    } catch (error: any) {
      console.error('Error generating CV:', error);
      setError(error.message || 'Gagal generate CV. Pastikan nama tersedia di database.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isGenerating) {
      handleGenerate();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#1A1E21] border-2 border-brand-yellow rounded-2xl shadow-2xl shadow-brand-yellow/20 w-full max-w-md mx-4 animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-brand-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-brand-yellow/10 rounded-lg">
              <UserCircle size={24} className="text-brand-yellow" />
            </div>
            <h2 className="text-xl font-bold text-white">Generate CV Profile</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/5"
            disabled={isGenerating}
          >
            <X size={24} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          <div>
            <label htmlFor="professorName" className="block text-sm font-semibold text-gray-300 mb-3">
              Masukkan nama profesor, lecturer, atau siapa saja:
            </label>
            <input
              id="professorName"
              type="text"
              value={professorName}
              onChange={(e) => {
                setProfessorName(e.target.value);
                setError(null);
              }}
              onKeyPress={handleKeyPress}
              placeholder="Contoh: Prof. Dr. Riri Fitri Sari"
              className="w-full px-4 py-3 bg-brand-dark border border-brand-border rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-brand-yellow transition-colors"
              disabled={isGenerating}
              autoFocus
            />
            <p className="text-xs text-gray-500 mt-2">
              💡 Tip: Masukkan nama lengkap untuk hasil yang lebih akurat
            </p>
          </div>

          {error && (
            <div className="p-4 bg-red-900/30 border border-red-700 text-red-300 rounded-xl text-sm flex items-start gap-2 animate-in fade-in slide-in-from-top duration-300">
              <X size={18} className="mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Info Box */}
          <div className="p-4 bg-brand-yellow/10 border border-brand-yellow/30 rounded-xl">
            <p className="text-sm text-gray-300 leading-relaxed">
              <span className="font-semibold text-brand-yellow">Apa yang akan dibuat?</span>
              <br />
              Sistem akan menghasilkan CV/profil profesional dalam format PDF yang berisi informasi lengkap tentang orang yang Anda cari dari database akademik.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 p-6 border-t border-brand-border">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 bg-brand-dark text-gray-300 font-semibold rounded-xl hover:bg-brand-dark/70 transition-all duration-200 border border-brand-border"
            disabled={isGenerating}
          >
            Batal
          </button>
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !professorName.trim()}
            className="flex-1 px-4 py-3 bg-brand-red text-white font-bold rounded-xl hover:bg-brand-red-dark hover:shadow-lg hover:shadow-brand-red/50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transform hover:scale-105"
          >
            {isGenerating ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Download size={18} />
                <span>Generate PDF</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}