"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Menu,
  X,
  MessageSquare,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { SuggestedQuestions } from "@/components/chat/SuggestedQuestions";
import { Sidebar } from "@/components/Sidebar";
import { useChat } from "@/hooks/useChat";
import { cn } from "@/lib/utils";
import { ChatInput } from "@/components/chat/ChatInput";

function EmptyState({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <div className="h-full flex flex-col items-center justify-center p-4 md:p-8">
      {/* Logo with glow */}
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="relative mb-8"
      >
        <div className="absolute inset-0 bg-gradient-primary rounded-3xl blur-3xl opacity-30 animate-pulse-slow" />
        <div className="relative w-20 h-20 rounded-3xl bg-gradient-primary flex items-center justify-center text-white font-bold text-3xl shadow-2xl shadow-primary/30">
          F
        </div>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="absolute -top-1 -right-1 w-5 h-5 bg-emerald-400 border-2 border-surface rounded-full"
        />
      </motion.div>

      {/* Title */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        className="text-center mb-2"
      >
        <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-2 tracking-tight">
          Your intelligent banking assistant
        </h1>
        <p className="text-sm text-muted-foreground max-w-lg mx-auto leading-relaxed">
          Ask me anything about <span className="text-pink-400 font-medium">bKash</span>,{" "}
          <span className="text-orange-400 font-medium">Nagad</span>, or{" "}
          <span className="text-blue-400 font-medium">DBBL</span>.
          <br />
          I understand Bengali, English, and Banglish.
        </p>
      </motion.div>

      {/* Feature badges */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
        className="flex flex-wrap items-center justify-center gap-2 mb-8 mt-4"
      >
        {[
          { icon: Zap, label: "Instant answers", color: "text-emerald-400" },
          { icon: ShieldCheck, label: "RAG powered", color: "text-cyan-400" },
          { icon: TrendingUp, label: "Bangla support", color: "text-violet-400" },
        ].map((feature) => (
          <div
            key={feature.label}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/5 text-xs text-muted-foreground"
          >
            <feature.icon className={cn("w-3.5 h-3.5", feature.color)} />
            {feature.label}
          </div>
        ))}
      </motion.div>

      {/* Suggested questions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
        className="w-full max-w-lg"
      >
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-primary" />
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Try asking
          </h3>
        </div>
        <SuggestedQuestions onSelect={onSelect} />
      </motion.div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-surface pointer-events-none" />
    </div>
  );
}

// Mobile Header
function MobileHeader({
  onMenuClick,
  sidebarOpen,
}: {
  onMenuClick: () => void;
  sidebarOpen: boolean;
}) {
  return (
    <div className="md:hidden flex items-center justify-between px-4 py-3 border-b border-border bg-surface/80 backdrop-blur-2xl">
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={onMenuClick}
        className="h-9 w-9 rounded-xl flex items-center justify-center bg-white/5 border border-border text-muted-foreground hover:text-foreground hover:bg-white/10 transition-all duration-200"
      >
        {sidebarOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
      </motion.button>

      <div className="flex items-center gap-2.5">
        <div className="relative">
          <div className="w-7 h-7 rounded-lg bg-gradient-primary flex items-center justify-center text-white font-bold text-xs">
            F
          </div>
          <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-emerald-400 border-2 border-surface rounded-full" />
        </div>
        <span className="text-sm font-semibold text-foreground">FinBot BD</span>
      </div>

      <div className="w-9" />
    </div>
  );
}

export default function Home() {
  const { messages, loading, error, send, clearChat } = useChat();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const hasMessages = messages.length > 0;

  const handleSuggestion = useCallback(
    (question: string) => {
      send(question);
    },
    [send]
  );

  return (
    <main className="flex h-screen overflow-hidden bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden md:block shrink-0">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setSidebarOpen(false)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden"
            />
            <motion.div
              initial={{ x: -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
              className="fixed left-0 top-0 h-full z-50 md:hidden"
            >
              <Sidebar onClose={() => setSidebarOpen(false)} />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {/* Grid background */}
        <div className="absolute inset-0 bg-grid pointer-events-none opacity-30" />

        {/* Glow orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -left-40 w-80 h-80 bg-primary/5 rounded-full blur-[100px]" />
          <div className="absolute -bottom-40 -right-40 w-80 h-80 bg-accent/5 rounded-full blur-[100px]" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary/[0.02] rounded-full blur-[150px]" />
        </div>

        {/* Mobile Header */}
        <MobileHeader
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
        />

        {/* Content */}
        <div className="flex-1 relative z-10 min-h-0">
          {!hasMessages ? (
            <EmptyState onSelect={handleSuggestion} />
          ) : (
            <ChatWindow
              messages={messages}
              loading={loading}
              error={error}
              onSend={send}
              onClear={clearChat}
            />
          )}
        </div>

        {/* If empty state, show a sticky input at the bottom */}
        {!hasMessages && (
          <div className="relative z-10 pb-4 px-4">
            <div className="max-w-lg mx-auto">
              <ChatInput onSend={handleSuggestion} loading={loading} />
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

