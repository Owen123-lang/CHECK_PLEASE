"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, X, Search as SearchIcon } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'chatbot';
  content: string;
  sessionId?: string;
}

interface ChatPanelProps {
  onSessionUpdate?: (sessionId: string) => void;
  onMessageUpdate?: (message: string) => void;
  onSendMessage?: (message: string) => Promise<string | null>;
  notebookId?: string;
  isLoadingPreviousChats?: boolean;
  previousChats?: PreviousChat[];
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
}

interface PreviousChat {
  id: number;
  notebookId: string;  // Changed to string (UUID)
  sender: string;
  body: string;
  created_at: string;
}

export default function ChatPanel({
  onSessionUpdate,
  onMessageUpdate,
  onSendMessage,
  notebookId,
  isLoadingPreviousChats = false,
  previousChats = [],
  searchQuery = '',
  onSearchChange
}: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sourceUrls, setSourceUrls] = useState<string[]>([]);
  const [tempUrl, setTempUrl] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [localSearchQuery, setLocalSearchQuery] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Control search bar visibility from parent
  const isSearchOpen = searchQuery === 'active';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Load previous chats into message display
  useEffect(() => {
    if (previousChats && previousChats.length > 0) {
      const loadedMessages: Message[] = previousChats.map((chat) => ({
        id: chat.id.toString(),
        role: (chat.sender === 'user' ? 'user' : 'chatbot') as 'user' | 'chatbot',
        content: chat.body,
      }));
      setMessages(loadedMessages);
      scrollToBottom();
    }
  }, [previousChats]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: String(Date.now()),
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setSourceUrls([]);
    setIsLoading(true);
    setError(null);

    try {
      if (!onSendMessage) {
        throw new Error('Message handler not available');
      }

      // Send message and get AI response
      const aiResponse = await onSendMessage(userInput);
      
      if (aiResponse) {
        const assistantMessage: Message = {
          id: String(Date.now() + 1),
          role: 'chatbot',
          content: aiResponse,
        };
        setMessages((prev) => [...prev, assistantMessage]);
        if (onMessageUpdate) {
          onMessageUpdate(assistantMessage.content);
        }
      }
    } catch (err: any) {
      console.error("Chat error:", err);
      const errorMessageContent = `⚠️ Error: ${err.message || 'Failed to get AI response'}. Please check your connection and try again.`;
      setError(errorMessageContent);
      
      const errorMessage: Message = {
        id: String(Date.now() + 1),
        role: 'chatbot',
        content: errorMessageContent
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      scrollToBottom();
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

  // Filter messages based on search query
  const filteredMessages = localSearchQuery.trim()
    ? messages.filter(msg =>
        msg.content.toLowerCase().includes(localSearchQuery.toLowerCase())
      )
    : messages;

  const highlightText = (text: string, query: string) => {
    if (!query.trim()) return text;
    
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark class="bg-brand-yellow text-black px-1 rounded">$1</mark>');
  };

  useEffect(() => {
    if (isSearchOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearchOpen]);

  useEffect(() => {
    if (!isSearchOpen) {
      setLocalSearchQuery('');
    }
  }, [isSearchOpen]);

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-brand-dark">
      {/* Search Bar */}
      {isSearchOpen && (
        <div className="bg-brand-container border-b-2 border-brand-border p-4 animate-in fade-in slide-in-from-top duration-300">
          <div className="max-w-4xl mx-auto flex items-center gap-3">
            <SearchIcon size={20} className="text-brand-yellow" />
            <input
              ref={searchInputRef}
              type="text"
              value={localSearchQuery}
              onChange={(e) => setLocalSearchQuery(e.target.value)}
              placeholder="Search in conversation..."
              className="flex-1 bg-brand-dark text-white placeholder-gray-500 rounded-lg p-3 border-2 border-brand-border outline-none focus:border-brand-yellow transition-colors"
            />
            <button
              onClick={() => {
                setLocalSearchQuery('');
                if (onSearchChange) onSearchChange('');
              }}
              className="text-gray-400 hover:text-white transition-colors p-2"
            >
              <X size={20} />
            </button>
          </div>
          {localSearchQuery && (
            <div className="max-w-4xl mx-auto mt-2 text-sm text-gray-400">
              Found {filteredMessages.length} message{filteredMessages.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>
      )}

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
          <>
            {localSearchQuery && filteredMessages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center px-4">
                <SearchIcon className="w-16 h-16 text-gray-600 mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No messages found</h3>
                <p className="text-gray-400">Try a different search term</p>
              </div>
            ) : (
              filteredMessages.map((m: Message) => (
                <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom duration-300`}>
                  <div className={`p-3 lg:p-4 rounded-2xl shadow-lg max-w-[85%] lg:max-w-2xl break-words whitespace-pre-wrap ${
                    m.role === 'user'
                      ? 'bg-brand-red text-white'
                      : 'bg-brand-container text-white border border-brand-border'
                  }`}>
                    {m.role === 'chatbot' ? (
                      <div
                        className="[&_*]:text-white [&_mark]:text-black"
                        dangerouslySetInnerHTML={{
                          __html: localSearchQuery ? highlightText(m.content, localSearchQuery) : m.content
                        }}
                      />
                    ) : (
                      localSearchQuery ? (
                        <div dangerouslySetInnerHTML={{ __html: highlightText(m.content, localSearchQuery) }} />
                      ) : (
                        m.content
                      )
                    )}
                  </div>
                </div>
              ))
            )}
          </>
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
                placeholder={notebookId ? "Search for an academic expert (e.g., Prof. Riri Fitri Sari)..." : "Select a notebook first..."}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading || !notebookId}
              />
              <button 
                type="submit" 
                className="bg-brand-yellow text-[#1A1E21] font-bold py-2 lg:py-3 px-4 lg:px-6 rounded-xl hover:bg-brand-yellow-dark hover:shadow-lg hover:shadow-brand-yellow/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 text-sm lg:text-base"
                disabled={isLoading || !notebookId}
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
