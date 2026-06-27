"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Menu,
  X,
} from "lucide-react";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { SuggestedQuestions } from "@/components/chat/SuggestedQuestions";
import { Sidebar } from "@/components/Sidebar";
import { ChatInput } from "@/components/chat/ChatInput";
import { useChat } from "@/hooks/useChat";
import { cn } from "@/lib/utils";

function EmptyState({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <div className="w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
        className="flex flex-col items-center text-center mb-10 md:mb-14"
      >
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          className="w-16 h-16 md:w-20 md:h-20 rounded-lg bg-accent flex items-center justify-center text-bg font-bold text-2xl md:text-3xl shadow-lg mb-6"
        >
          F
        </motion.div>

        {/* Title */}
        <h1 className="text-xl sm:text-2xl md:text-3xl font-heading font-semibold text-text tracking-tight mb-3">
          Welcome to FinBot BD
        </h1>

        {/* Description */}
        <p className="text-sm md:text-base text-text-secondary max-w-lg leading-relaxed mb-4">
          Your AI banking assistant for regional services.
          <br />
          Get instant answers about banking services, cards, PIN reset,
          accounts, transfers, and more.
        </p>

        {/* Multilingual Badge */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-card border border-accent/15">
          <span className="text-xs font-medium text-text-secondary">
            Supports English &middot; বাংলা &middot; Banglish
          </span>
        </div>
      </motion.div>

      {/* Chat Input — primary CTA */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.3, ease: "easeOut" }}
        className="max-w-2xl mx-auto mb-10 md:mb-14"
      >
        <ChatInput onSend={onSelect} loading={false} />
      </motion.div>

      {/* Separator — full width, centered */}
      <div className="w-full flex items-center gap-4 mb-10 md:mb-14">
        <div className="flex-1 h-px bg-divider" />
        <span className="text-xs text-text-muted font-medium uppercase tracking-widest shrink-0">or</span>
        <div className="flex-1 h-px bg-divider" />
      </div>

      {/* Try Asking Section */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.3, ease: "easeOut" }}
        className="pb-16 md:pb-24"
      >
        <div className="text-center mb-8 md:mb-10">
          <h3 className="text-sm font-heading font-semibold text-text tracking-tight">
            Try Asking
          </h3>
          <p className="text-xs text-text-secondary mt-1.5">
            Choose an example below to get started.
          </p>
        </div>

        <SuggestedQuestions onSelect={onSelect} />
      </motion.div>
    </div>
  );
}

function MobileHeader({
  onMenuClick,
  sidebarOpen,
}: {
  onMenuClick: () => void;
  sidebarOpen: boolean;
}) {
  return (
    <div className="md:hidden flex items-center justify-between px-4 py-3 border-b border-divider bg-bg/80 backdrop-blur-md">
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onMenuClick}
        className="h-9 w-9 rounded-md flex items-center justify-center bg-card border border-border text-text-secondary hover:text-text transition-all duration-200"
      >
        {sidebarOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
      </motion.button>

      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded bg-accent flex items-center justify-center text-bg font-bold text-xs">
          F
        </div>
        <span className="text-sm font-medium text-text">FinBot BD</span>
      </div>

      <div className="w-9" />
    </div>
  );
}

export default function Home() {
  const { messages, loading, error, send, clearChat, goHome } = useChat();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const hasMessages = messages.length > 0;

  const handleSuggestion = useCallback(
    (question: string) => {
      send(question);
    },
    [send]
  );

  return (
    <main className="flex h-screen overflow-hidden bg-bg">
      {/* Desktop Sidebar — fixed 280px */}
      <div className="hidden md:block shrink-0">
        <Sidebar onLogoClick={goHome} />
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              onClick={() => setSidebarOpen(false)}
              className="fixed inset-0 bg-overlay/60 backdrop-blur-sm z-40 md:hidden"
            />
            <motion.div
              initial={{ x: -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="fixed left-0 top-0 h-full z-50 md:hidden"
            >
              <Sidebar onLogoClick={goHome} />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Subtle grid background */}
        <div
          className="absolute inset-0 pointer-events-none opacity-[0.015]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(240,234,224,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(240,234,224,0.3) 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />

        {/* Mobile Header */}
        <MobileHeader
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
        />

        {/* Content Area */}
        <div className="flex-1 relative z-10 min-h-0">
          <AnimatePresence mode="wait">
            {!hasMessages ? (
              /* ─────────────────────────────────────────────
                 WELCOME LAYOUT
                 Natural height, scrollable, generous spacing
                 ───────────────────────────────────────────── */
              <motion.div
                key="welcome"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="h-full overflow-y-auto scrollbar-hide"
              >
                <EmptyState onSelect={handleSuggestion} />
              </motion.div>
            ) : (
              /* ─────────────────────────────────────────────
                 CONVERSATION LAYOUT
                 Fixed header + scrollable messages + fixed input
                 ───────────────────────────────────────────── */
              <motion.div
                key="chat"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                <ChatWindow
                  messages={messages}
                  loading={loading}
                  error={error}
                  onSend={send}
                  onClear={clearChat}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </main>
  );
}