"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowUp, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  autoFocus?: boolean;
  onSend: (message: string) => void;
  loading: boolean;
}

export function ChatInput({ onSend, loading, autoFocus }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (autoFocus && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [autoFocus]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [input]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const canSend = input.trim().length > 0 && !loading;

  return (
    <div className="relative w-full">
      <div
        className={cn(
          "relative flex items-center gap-3 rounded-lg border transition-all duration-200",
          "bg-card/80 backdrop-blur-sm",
          canSend
            ? "border-accent/40 shadow-[0_0_20px_-5px_rgba(184,115,51,0.2)]"
            : "border-border"
        )}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about bKash, Nagad, DBBL..."
          disabled={loading}
          rows={1}
          className={cn(
            "flex-1 bg-transparent border-0 outline-none resize-none py-3.5 px-4",
            "text-sm text-text placeholder-text-muted",
            "focus:ring-0 focus:outline-none",
            "disabled:opacity-30 disabled:cursor-not-allowed",
            "scrollbar-hide",
            "min-h-[48px] max-h-[160px]"
          )}
        />

        <motion.button
          whileHover={canSend ? { scale: 1.05 } : undefined}
          whileTap={canSend ? { scale: 0.95 } : undefined}
          onClick={handleSubmit}
          disabled={!canSend}
          aria-label="Send message"
          className={cn(
            "h-10 w-10 rounded-lg flex items-center justify-center shrink-0 mr-2 transition-all duration-200",
            canSend
              ? "bg-accent text-bg hover:bg-accent-hover shadow-[0_2px_8px_rgba(184,115,51,0.3)]"
              : "bg-white/[0.04] text-text-muted cursor-not-allowed"
          )}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <ArrowUp className="w-4 h-4" />
          )}
        </motion.button>
      </div>

      <p className="text-2xs text-text-muted text-center mt-2">
        Press Enter to send · Shift + Enter for new line
      </p>
    </div>
  );
}