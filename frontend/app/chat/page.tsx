"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Header from "@/components/chat/Header";
import SourcePanel from "@/components/chat/SourcePanel";
import ChatPanel from "@/components/chat/ChatPanel";
import ProtectedRoute from "@/components/auth/ProtectedRoute";

interface PreviousChat {
  id: number;
  notebookId: number;
  sender: string;
  body: string;
  created_at: string;
}

export default function Home() {
  const searchParams = useSearchParams();
  const notebookId = searchParams.get("notebook");
  
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [lastAssistantMessage, setLastAssistantMessage] = useState<string | null>(null);
  const [previousChats, setPreviousChats] = useState<PreviousChat[]>([]);
  const [isLoadingChats, setIsLoadingChats] = useState(false);
  const [notebookTitle, setNotebookTitle] = useState<string>("");

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
        `http://localhost:4000/api/chat/notebook/${notebookId}`,
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
      const response = await fetch(
        `http://localhost:4000/api/notebooks/${notebookId}`,
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
      const userResponse = await fetch('http://localhost:4000/api/chat', {
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
      const aiResponse = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          notebookId: notebookId,
        }),
      });

      const aiData = await aiResponse.json();
      const assistantResponse = aiData.response || aiData.message || 'No response from AI';

      // Step 3: Save AI response to database
      const assistantSaveResponse = await fetch('http://localhost:4000/api/chat', {
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

  return (
    <ProtectedRoute>
      <div className="flex flex-col h-screen bg-brand-dark text-brand-text">
        <Header notebookTitle={notebookTitle} />
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
          />
        </main>
      </div>
    </ProtectedRoute>
  );
}
