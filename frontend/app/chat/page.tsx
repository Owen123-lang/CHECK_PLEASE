"use client";

import { useState } from "react";
import Header from "@/components/chat/Header";
import SourcePanel from "@/components/chat/SourcePanel";
import ChatPanel from "@/components/chat/ChatPanel";
import StudioPanel from "@/components/chat/StudioPanel";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [lastAssistantMessage, setLastAssistantMessage] = useState<string | null>(null);

  return (
    <div className="flex flex-col h-screen bg-brand-dark text-brand-text">
      <Header />
      <main className="flex flex-1 overflow-hidden">
        {/* Kolom Kiri: Sources (Sidebar) */}
        <SourcePanel />
        
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
  );
}
