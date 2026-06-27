"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trash2,
  ChevronDown,
} from "lucide-react";
import { Message } from "@/types";
import { ChatInput } from "./ChatInput";
import { MessageBubble } from "./MessageBubble";
import { SuggestedQuestions } from "./SuggestedQuestions";
import { cn } from "@/lib/utils";

interface ChatWindowProps {
  messages: Message[];
  loading: boolean;
  error: string | null;
  onSend: (message: string) => void;
  onClear: () => void;
  isEmpty?: boolean;
  title?: string;
}

const STATUS_STAGES = [
  "Detecting language...",
  "Identifying banking service...",
  "Searching knowledge base...",
  "Ranking relevant information...",
  "Generating response...",
];

function Dot({ delay }: { delay: number }) {
  return (
    <motion.span
      className="block w-2 h-2 rounded-full"
      style={{ backgroundColor: "#B87333" }}
      animate={{
        opacity: [0.45, 1, 0.45],
        scale: [1, 1.15, 1],
      }}
      transition={{
        duration: 1.4,
        repeat: Infinity,
        delay,
        ease: "easeInOut",
      }}
    />
  );
}

function TypingIndicator() {
  const [statusIndex, setStatusIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStatusIndex((prev) => (prev + 1) % STATUS_STAGES.length);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.18, ease: "easeOut" }}
      className="flex gap-3 items-start"
    >
      {/* Bot Avatar */}
      <div className="shrink-0 mt-0.5">
        <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center text-bg font-bold text-sm">
          F
        </div>
      </div>

      {/* Thinking bubble */}
      <div className="bg-surface border border-border rounded-lg rounded-tl-sm px-4 py-3 min-w-[160px]">
        <div className="flex items-center gap-3">
          {/* Three copper dots */}
          <div className="flex items-center gap-1.5 shrink-0">
            <Dot delay={0} />
            <Dot delay={0.2} />
            <Dot delay={0.4} />
          </div>

          {/* Dynamic status */}  
          <AnimatePresence mode="popLayout">
            <motion.span
              key={statusIndex}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.15, ease: "easeOut" }}
              className="text-xs text-text-secondary font-medium whitespace-nowrap"
            >
              {STATUS_STAGES[statusIndex]}
            </motion.span>
          </AnimatePresence>
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
      className="flex items-start gap-3 px-4 py-3 rounded-lg bg-danger/10 border border-danger/20"
    >
      <div className="w-2 h-2 rounded-full bg-danger mt-1.5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-danger">Error</p>
        <p className="text-xs text-danger/80 mt-0.5">{error}</p>
      </div>
    </motion.div>
  );
}

function ScrollToBottom({ onClick }: { onClick: () => void }) {
  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="absolute bottom-4 left-1/2 -translate-x-1/2 h-8 px-3 rounded-lg bg-card/90 backdrop-blur-sm border border-border text-text-secondary hover:text-text flex items-center gap-1.5 text-xs shadow-lg transition-all duration-200"
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
  isEmpty,
  title = "New Conversation",
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
      {/* Sticky Header — aligned with messages and input */}
      <div className="sticky top-0 z-20 bg-bg/80 backdrop-blur-md border-b border-divider">
        <div className="flex items-center justify-between px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-md bg-accent flex items-center justify-center text-bg font-bold text-sm">
              F
            </div>
            <div>
              <h2 className="text-sm font-medium text-text">
              <AnimatePresence mode="wait">
                <motion.span
                  key={title}
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 4 }}
                  transition={{ duration: 0.2 }}
                >
                  {title}
                </motion.span>
              </AnimatePresence>
            </h2>
              <div className="flex items-center gap-1.5">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-60" />
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-success" />
                </span>
                <span className="text-2xs text-text-secondary">Online</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            {messages.length > 0 && (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onClear}
                className="h-8 px-3 rounded-md text-xs font-medium text-text-secondary hover:text-text hover:bg-white/[0.03] transition-all duration-200 flex items-center gap-1.5"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Clear
              </motion.button>
            )}
          </div>
        </div>
      </div>

      {/* Messages — fluid layout with comfortable padding */}
      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto scrollbar-hide relative"
      >
        <div className="px-4 sm:px-6 lg:px-8 py-4 space-y-5">
          {isEmpty ? (
            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col items-center justify-center text-center py-12"
            >
              <div className="w-16 h-16 rounded-xl bg-accent flex items-center justify-center text-bg font-bold text-2xl mb-6 shadow-lg">
                F
              </div>
              <h2 className="text-xl sm:text-2xl font-heading font-semibold text-text tracking-tight mb-2">
                Hello! 
              </h2>
              <p className="text-sm md:text-base text-text-secondary max-w-md leading-relaxed mb-1">
                I'm FinBot, your Intelligent Banking Assistant.
              </p>
              <p className="text-sm md:text-base text-text-secondary max-w-md leading-relaxed mb-8">
                How can I assist you today?
              </p>
              <div className="w-full max-w-2xl">
                <SuggestedQuestions onSelect={onSend} />
              </div>
            </motion.div>
          ) : (
            <AnimatePresence mode="popLayout">
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
            </AnimatePresence>
          )}

          <AnimatePresence>
            {loading && <TypingIndicator />}
          </AnimatePresence>

          {error && <ErrorBanner error={error} />}

          <div ref={bottomRef} />
        </div>

        <AnimatePresence>
          {showScrollBtn && (
            <ScrollToBottom onClick={scrollToBottom} />
          )}
        </AnimatePresence>
      </div>

      {/* Sticky Input — fluid, aligned with messages */}
      <div className="sticky bottom-0 z-20 bg-gradient-to-t from-bg via-bg/95 to-transparent pt-6 pb-3 px-4 sm:px-6 lg:px-8">
        <ChatInput onSend={onSend} loading={loading} autoFocus={isEmpty} />
      </div>
    </div>
  );
}