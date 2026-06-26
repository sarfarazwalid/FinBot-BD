"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trash2,
  ChevronDown,
} from "lucide-react";
import { Message } from "@/types";
import { ChatInput } from "./ChatInput";
import { MessageBubble } from "./MessageBubble";

interface ChatWindowProps {
  messages: Message[];
  loading: boolean;
  error: string | null;
  onSend: (message: string) => void;
  onClear: () => void;
}

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="flex gap-3"
    >
      <div className="relative shrink-0 mt-0.5">
        <div className="w-8 h-8 rounded-xl bg-gradient-primary flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-primary/20">
          F
        </div>
        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-400 border-2 border-surface rounded-full" />
      </div>
      <div className="glass-strong rounded-2xl rounded-tl-md px-4 py-3 min-w-[80px]">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <motion.span
              animate={{ y: [0, -4, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
              className="w-2 h-2 bg-primary rounded-full"
            />
            <motion.span
              animate={{ y: [0, -4, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: 0.15 }}
              className="w-2 h-2 bg-primary rounded-full"
            />
            <motion.span
              animate={{ y: [0, -4, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: 0.3 }}
              className="w-2 h-2 bg-primary rounded-full"
            />
          </div>
          <span className="text-2xs text-muted-foreground">Thinking...</span>
        </div>
      </div>
    </motion.div>
  );
}

function ErrorBanner({ error }: { error: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -8, scale: 0.95 }}
      className="flex items-start gap-3 px-4 py-3 rounded-xl bg-rose/10 border border-rose/20"
    >
      <div className="w-2 h-2 rounded-full bg-rose mt-1.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-rose-300">Error</p>
        <p className="text-xs text-rose-200/70 mt-0.5">{error}</p>
      </div>
    </motion.div>
  );
}

function ScrollToBottom({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className="absolute bottom-4 left-1/2 -translate-x-1/2 h-8 px-3 rounded-xl bg-surface-elevated/90 backdrop-blur-xl border border-border text-muted-foreground hover:text-foreground flex items-center gap-1.5 text-xs shadow-lg transition-all duration-200"
    >
      <ChevronDown className="w-3.5 h-3.5" />
      Scroll to bottom
    </motion.button>
  );
}

export function ChatWindow({
  messages,
  loading,
  error,
  onSend,
  onClear,
}: ChatWindowProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [showScrollBtn, setShowScrollBtn] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollBtn(!isNearBottom);
    };

    container.addEventListener("scroll", handleScroll);
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (!showScrollBtn && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading, showScrollBtn]);

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Sticky Header */}
      <div className="sticky top-0 z-20 backdrop-blur-2xl bg-surface/60 border-b border-border">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-9 h-9 rounded-xl bg-gradient-primary flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-primary/20">
                F
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-400 border-2 border-surface rounded-full" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-foreground">FinBot BD</h2>
              <div className="flex items-center gap-1.5">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-400" />
                </span>
                <span className="text-2xs text-emerald-400">Online</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {messages.length > 0 && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onClear}
                className="h-8 px-3 rounded-lg text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200 flex items-center gap-1.5"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Clear
              </motion.button>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto scroll-area relative"
      >
        <div className="px-4 py-4 space-y-5 max-w-3xl mx-auto">
          <AnimatePresence mode="popLayout">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </AnimatePresence>

          <AnimatePresence>
            {loading && <TypingIndicator />}
          </AnimatePresence>

          {error && <ErrorBanner error={error} />}

          <div ref={bottomRef} />
        </div>

        {/* Scroll to bottom button */}
        <AnimatePresence>
          {showScrollBtn && (
            <ScrollToBottom onClick={scrollToBottom} />
          )}
        </AnimatePresence>
      </div>

      {/* Sticky Input Area */}
      <div className="sticky bottom-0 z-20 bg-gradient-surface pt-2 pb-3 px-4">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSend={onSend} loading={loading} />
        </div>
      </div>
    </div>
  );
}