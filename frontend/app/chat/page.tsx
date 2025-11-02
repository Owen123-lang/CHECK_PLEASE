import Header from "@/components/chat/Header";
import SourcePanel from "@/components/chat/SourcePanel";
import ChatPanel from "@/components/chat/ChatPanel";
import StudioPanel from "@/components/chat/StudioPanel";

export default function Home() {
  return (
    <div className="flex flex-col h-screen bg-brand-dark text-brand-text">
      <Header />
      <main className="flex flex-1 overflow-hidden">
        {/* Kolom Kiri: Sources (Sidebar) */}
        <SourcePanel />
        
        {/* Kolom Tengah: Chat (Main) */}
        <ChatPanel />
        
        {/* Kolom Kanan: Studio (Tools) */}
        <StudioPanel />
      </main>
    </div>
  );
}
