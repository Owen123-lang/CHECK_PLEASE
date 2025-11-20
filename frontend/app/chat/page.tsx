"use client";

import { useState } from "react";
import Header from "@/components/chat/Header";
import SourcePanel from "@/components/chat/SourcePanel";
import ChatPanel from "@/components/chat/ChatPanel";
import StudioPanel from "@/components/chat/StudioPanel";
import ProtectedRoute from "@/components/auth/ProtectedRoute";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [lastAssistantMessage, setLastAssistantMessage] = useState<string | null>(null);

  const handlePdfUploaded = (filename: string) => {
    console.log('PDF uploaded:', filename);
    // You can add additional logic here if needed
  };

  return (
    <ProtectedRoute>
      <div className="flex flex-col h-screen bg-brand-dark text-brand-text">
        <Header />
        <main className="flex flex-1 overflow-hidden">
          {/* Kolom Kiri: Sources (Sidebar) */}
          <SourcePanel
            sessionId={sessionId}
            onPdfUploaded={handlePdfUploaded}
          />
          
          {/* Kolom Tengah: Chat (Main) */}
          <ChatPanel
            onSessionUpdate={setSessionId}
            onMessageUpdate={setLastAssistantMessage}
          />
          
          {/* Kolom Kanan: Studio (Tools) */}
          <StudioPanel
            sessionId={sessionId}
            lastMessage={lastAssistantMessage}
          />
        </main>
      </div>
    </ProtectedRoute>
  );
}
