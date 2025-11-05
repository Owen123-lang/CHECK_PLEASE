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
      <div className="flex-1 p-6 space-y-4 overflow-y-auto custom-scrollbar">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <h2 className="text-3xl font-bold text-brand-yellow mb-2">Check Please</h2>
            <p className="text-lg">Your Academic Research Assistant for DTE UI</p>
            <p className="text-sm mt-2">Ready to search academic profiles. Start by asking about a professor or researcher.</p>
            <div className="mt-6 p-4 bg-gray-800 rounded-lg max-w-md">
              <p className="text-brand-yellow font-semibold mb-2">💡 Try asking:</p>
              <p className="text-sm text-gray-400">"Tell me about Prof. Dr. Riri Fitri Sari"</p>
              <p className="text-xs text-gray-500 mt-2">Then click "Export Profile to PDF" in the Studio panel →</p>
            </div>
          </div>
        ) : (
          messages.map((m: Message) => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`p-4 rounded-xl shadow-md max-w-2xl break-words whitespace-pre-wrap ${
                m.role === 'user' 
                  ? 'bg-brand-red text-white' 
                  : 'bg-gray-800 text-gray-200'
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
           <div className="flex justify-start">
             <div className="bg-gray-800 text-gray-400 p-4 rounded-xl shadow-md flex items-center space-x-2">
                <Loader2 size={20} className="animate-spin text-brand-yellow" />
                <span>AI is researching academic profiles...</span>
             </div>
           </div>
        )}
        {error && (
            <div className="flex justify-start">
              <div className="bg-red-900 text-red-300 p-4 rounded-xl shadow-md">
                {error}
              </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* UI untuk menambahkan URL */}
      <div className="p-4 border-t border-brand-border bg-brand-dark">
        <div className="mb-3">
          <div className="flex items-center space-x-2 mb-2">
            <input
              type="text"
              className="flex-1 bg-gray-800 text-white placeholder-gray-500 rounded-lg p-2 border border-brand-border outline-none focus:border-brand-yellow"
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
              className="bg-gray-700 text-white py-2 px-4 rounded-lg hover:bg-gray-600 transition-colors"
            >
              Add URL
            </button>
          </div>
          {sourceUrls.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {sourceUrls.map((url, index) => (
                <div key={index} className="bg-gray-700 text-sm text-yellow-400 rounded-full py-1 px-3 flex items-center gap-2">
                  <span className="max-w-xs truncate">{url.length > 40 ? url.substring(0, 40) + '...' : url}</span>
                  <button 
                    onClick={() => handleRemoveUrl(url)} 
                    className="text-red-500 hover:text-red-400"
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
          <div className="flex items-center bg-gray-800 rounded-xl p-2 border border-brand-border focus-within:border-brand-yellow shadow-inner">
            <input
              className="flex-1 bg-transparent text-white placeholder-gray-500 outline-none px-3 py-2"
              value={input}
              placeholder="Search for an academic expert (e.g., Prof. Riri Fitri Sari)..."
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="bg-brand-yellow text-black font-bold py-2 px-5 rounded-lg hover:bg-brand-yellow-dark transition-colors disabled:opacity-50 shadow-md flex items-center space-x-2"
              disabled={isLoading}
            >
              <Send size={18} /> <span>Send</span>
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
