"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Header from "@/components/chat/Header";
import SourcePanel from "@/components/chat/SourcePanel";
import ChatPanel from "@/components/chat/ChatPanel";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { API_ENDPOINTS } from "@/lib/api";

interface PreviousChat {
  id: number;
  notebookId: string;  // Changed to string (UUID)
  sender: string;
  body: string;
  created_at: string;
}

function ChatPageContent() {
  const searchParams = useSearchParams();
  const notebookId = searchParams.get("notebook");
  
  // Generate ONE persistent session ID for this notebook/tab session
  const [sessionId, setSessionId] = useState<string>(() => {
    // Generate UUID-like session ID on mount
    return `session_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  });
  const [lastAssistantMessage, setLastAssistantMessage] = useState<string | null>(null);
  const [previousChats, setPreviousChats] = useState<PreviousChat[]>([]);
  const [isLoadingChats, setIsLoadingChats] = useState(false);
  const [notebookTitle, setNotebookTitle] = useState<string>("");
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Fetch previous chats when notebook ID changes
  useEffect(() => {
    if (notebookId) {
      fetchPreviousChats();
      fetchNotebookTitle();
    }
  }, [notebookId]);

  const getAuthToken = () => {
    return localStorage.getItem('token');
  };

  const fetchPreviousChats = async () => {
    if (!notebookId) return;

    setIsLoadingChats(true);
    try {
      const token = getAuthToken();
      const response = await fetch(
        API_ENDPOINTS.CHAT_NOTEBOOK(notebookId),
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      const data = await response.json();
      
      if (data.success && data.payload) {
        setPreviousChats(Array.isArray(data.payload) ? data.payload : []);
        console.log(`Loaded ${data.payload?.length || 0} previous chats`);
      }
    } catch (error) {
      console.error("Error fetching previous chats:", error);
    } finally {
      setIsLoadingChats(false);
    }
  };

  const fetchNotebookTitle = async () => {
    if (!notebookId) return;

    try {
      const token = getAuthToken();
      
      // notebookId is now UUID string, no need to parse
      const response = await fetch(
        API_ENDPOINTS.NOTEBOOK(notebookId),
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      const data = await response.json();
      
      if (data.success && data.payload?.title) {
        setNotebookTitle(data.payload.title);
      }
    } catch (error) {
      console.error("Error fetching notebook title:", error);
    }
  };

  const handleSendMessage = async (userMessage: string): Promise<string | null> => {
    if (!notebookId || !userMessage.trim()) return null;

    try {
      const token = getAuthToken();

      // Step 1: Save user message to database
      const userResponse = await fetch(API_ENDPOINTS.CHAT, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          notebookId: notebookId,
          sender: 'user',
          body: userMessage,
        }),
      });

      const userData = await userResponse.json();
      if (!userData.success) {
        throw new Error('Failed to save user message');
      }

      // Step 2: Send to AI backend (port 8000) for processing
      console.log('Sending to AI backend:', userMessage);
      console.log('Using session_id:', sessionId);
      const aiResponse = await fetch(API_ENDPOINTS.AI_CHAT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          notebookId: notebookId,
          session_id: sessionId,  // CRITICAL: Pass same session_id used for PDF upload
        }),
      });

      const aiData = await aiResponse.json();
      const assistantResponse = aiData.response || aiData.message || 'No response from AI';

      // Step 3: Save AI response to database
      const assistantSaveResponse = await fetch(API_ENDPOINTS.CHAT, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          notebookId: notebookId,
          sender: 'chatbot',
          body: assistantResponse,
        }),
      });

      const assistantData = await assistantSaveResponse.json();
      if (assistantData.success) {
        setLastAssistantMessage(assistantResponse);
        // Refresh chats
        await fetchPreviousChats();
        return assistantResponse;
      }

      return assistantResponse;
    } catch (error) {
      console.error('Error in handleSendMessage:', error);
      throw error;
    }
  };

  const handlePdfUploaded = (filename: string) => {
    console.log('PDF uploaded:', filename);
  };

  const handleSearchClick = () => {
    setIsSearchOpen(prev => !prev);
  };

  const handleSearchClose = () => {
    setIsSearchOpen(false);
  };

  return (
    <ProtectedRoute>
      <div className="flex flex-col h-screen bg-brand-dark text-brand-text">
        <Header notebookTitle={notebookTitle} onSearchClick={handleSearchClick} />
        <main className="flex flex-1 overflow-hidden">
          {/* Kolom Kiri: Sources & Studio (Sidebar) */}
          <SourcePanel
            sessionId={sessionId}
            lastMessage={lastAssistantMessage}
            onPdfUploaded={handlePdfUploaded}
            notebookId={notebookId || undefined}
            previousChats={previousChats}
          />
          
          {/* Kolom Tengah: Chat (Main) */}
          <ChatPanel
            onSessionUpdate={setSessionId}
            onMessageUpdate={setLastAssistantMessage}
            onSendMessage={handleSendMessage}
            notebookId={notebookId || undefined}
            isLoadingPreviousChats={isLoadingChats}
            previousChats={previousChats}
            searchQuery={isSearchOpen ? 'active' : ''}
            onSearchChange={handleSearchClose}
          />
        </main>
      </div>
    </ProtectedRoute>
  );
}

export default function Home() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-screen bg-brand-dark">
        <div className="text-brand-yellow text-xl">Loading...</div>
      </div>
    }>
      <ChatPageContent />
    </Suspense>
  );
}
