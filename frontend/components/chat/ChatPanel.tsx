"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, X } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sessionId?: string;
}

interface ChatPanelProps {
  onSessionUpdate?: (sessionId: string) => void;
  onMessageUpdate?: (message: string) => void;
}

export default function ChatPanel({ onSessionUpdate, onMessageUpdate }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sourceUrls, setSourceUrls] = useState<string[]>([]);
  const [tempUrl, setTempUrl] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: String(Date.now()),
      role: 'user',
      content: input.trim()
    };

    const currentSourceUrls = sourceUrls;
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setSourceUrls([]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: userMessage.content,
          user_urls: currentSourceUrls.length > 0 ? currentSourceUrls : null,
          session_id: sessionId
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // Update session ID
      if (data.session_id) {
        setSessionId(data.session_id);
        onSessionUpdate?.(data.session_id);
      }
      
      const assistantMessage: Message = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: data.response || "Sorry, I couldn't get a valid response from the AI.",
        sessionId: data.session_id
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update last assistant message for CV generation
      onMessageUpdate?.(data.response);

    } catch (err: any) {
      console.error("Full chat error object:", err);
      const errorMessageContent = `Connection Error: Failed to fetch. Check the browser console (F12) for more details. Is the backend server running at http://127.0.0.1:8000?`;
      setError(errorMessageContent);
      
      const errorMessage: Message = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: errorMessageContent
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddUrl = () => {
    if (tempUrl.trim()) {
      setSourceUrls(prev => [...prev, tempUrl.trim()]);
      setTempUrl('');
    }
  };

  const handleRemoveUrl = (urlToRemove: string) => {
    setSourceUrls(prev => prev.filter(url => url !== urlToRemove));
  };

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-brand-dark">
      {/* Area Tampilan Chat */}
      <div className="flex-1 p-4 lg:p-6 space-y-4 overflow-y-auto custom-scrollbar">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="max-w-2xl">
              <h2 className="text-3xl lg:text-4xl font-bold text-brand-yellow mb-3">Check Please</h2>
              <p className="text-lg lg:text-xl text-gray-300 mb-2">Your Academic Research Assistant</p>
              <p className="text-sm lg:text-base text-gray-400 mb-8">Ready to search academic profiles. Start by asking about a professor or researcher.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
                <div className="p-4 lg:p-5 bg-brand-container rounded-xl border border-brand-border hover:border-brand-yellow/50 transition-all duration-300 hover:scale-105">
                  <p className="text-brand-yellow font-semibold mb-2 text-sm lg:text-base">💡 Try asking:</p>
                  <p className="text-sm text-gray-300">"Tell me about Prof. Dr. Riri Fitri Sari"</p>
                </div>
                <div className="p-4 lg:p-5 bg-brand-container rounded-xl border border-brand-border hover:border-brand-red/50 transition-all duration-300 hover:scale-105">
                  <p className="text-brand-red font-semibold mb-2 text-sm lg:text-base">📄 Next step:</p>
                  <p className="text-xs lg:text-sm text-gray-400">Click "Export Profile to PDF" in the Studio panel →</p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map((m: Message) => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom duration-300`}>
              <div className={`p-3 lg:p-4 rounded-2xl shadow-lg max-w-[85%] lg:max-w-2xl break-words whitespace-pre-wrap ${
                m.role === 'user' 
                  ? 'bg-brand-red text-white' 
                  : 'bg-brand-container text-gray-200 border border-brand-border'
              }`}>
                {m.role === 'assistant' ? (
                  <div dangerouslySetInnerHTML={{ __html: m.content }} />
                ) : (
                  m.content
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
           <div className="flex justify-start animate-in fade-in duration-300">
             <div className="bg-brand-container border border-brand-border text-gray-300 p-3 lg:p-4 rounded-2xl shadow-lg flex items-center space-x-3">
                <Loader2 size={20} className="animate-spin text-brand-yellow" />
                <span className="text-sm lg:text-base">AI is researching academic profiles...</span>
             </div>
           </div>
        )}
        {error && (
            <div className="flex justify-start animate-in fade-in duration-300">
              <div className="bg-red-900/50 border border-red-700 text-red-300 p-3 lg:p-4 rounded-2xl shadow-lg max-w-2xl">
                {error}
              </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* UI untuk menambahkan URL */}
      <div className="p-4 lg:p-6 border-t-2 border-brand-border bg-brand-container">
        <div className="max-w-4xl mx-auto">
          <div className="mb-4">
            <div className="flex items-center space-x-2 mb-3">
              <input
                type="text"
                className="flex-1 bg-brand-dark text-white placeholder-gray-500 rounded-xl p-3 border-2 border-brand-border outline-none focus:border-brand-yellow transition-colors text-sm lg:text-base"
                placeholder="Paste a URL source (e.g., Google Scholar profile)..."
                value={tempUrl}
                onChange={(e) => setTempUrl(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddUrl();
                  }
                }}
              />
              <button
                type="button"
                onClick={handleAddUrl}
                className="bg-brand-container border-2 border-brand-border text-white py-3 px-4 lg:px-6 rounded-xl hover:border-brand-yellow hover:bg-brand-dark transition-all duration-300 font-medium text-sm lg:text-base"
              >
                Add URL
              </button>
            </div>
            {sourceUrls.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {sourceUrls.map((url, index) => (
                  <div key={index} className="bg-brand-dark border border-brand-yellow/50 text-sm text-brand-yellow rounded-full py-1.5 px-4 flex items-center gap-2 hover:bg-brand-yellow/10 transition-colors">
                    <span className="max-w-xs truncate">{url.length > 40 ? url.substring(0, 40) + '...' : url}</span>
                    <button 
                      onClick={() => handleRemoveUrl(url)} 
                      className="text-red-500 hover:text-red-400 transition-colors"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Input Form Chat */}
          <form onSubmit={handleSubmit}>
            <div className="flex items-center bg-brand-dark rounded-2xl p-2 border-2 border-brand-border focus-within:border-brand-yellow transition-colors shadow-lg">
              <input
                className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none px-3 lg:px-4 py-2 lg:py-3 text-sm lg:text-base"
                value={input}
                placeholder="Search for an academic expert (e.g., Prof. Riri Fitri Sari)..."
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
              />
              <button 
                type="submit" 
                className="bg-brand-yellow text-[#1A1E21] font-bold py-2 lg:py-3 px-4 lg:px-6 rounded-xl hover:bg-brand-yellow-dark hover:shadow-lg hover:shadow-brand-yellow/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 text-sm lg:text-base"
                disabled={isLoading}
              >
                <Send size={18} /> <span className="hidden sm:inline">Send</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  );
}
