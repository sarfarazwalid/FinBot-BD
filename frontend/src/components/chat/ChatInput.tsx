"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Loader2,
  Mic,
  Paperclip,
  ArrowUp,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  loading: boolean;
}

export function ChatInput({ onSend, loading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [focused, setFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 160) + "px";
    }
  }, [input]);

  const handleSubmit = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [input, loading, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const canSend = input.trim().length > 0 && !loading;

  return (
    <div className="relative">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
        className={cn(
          "relative flex items-end gap-2 p-2 rounded-lg transition-all duration-200",
          "bg-card/80 backdrop-blur-sm border",
          focused ? "border-accent/40" : "border-border hover:border-accent/20"
        )}
      >
        {/* Left controls */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            className="h-8 w-8 rounded-md flex items-center justify-center text-text-muted hover:text-text-secondary hover:bg-white/[0.03] transition-all duration-200"
            title="Attach file"
          >
            <Paperclip className="w-4 h-4" />
          </button>
          <button
            type="button"
            className="h-8 w-8 rounded-md flex items-center justify-center text-text-muted hover:text-text-secondary hover:bg-white/[0.03] transition-all duration-200"
            title="Voice input"
          >
            <Mic className="w-4 h-4" />
          </button>
        </div>

        {/* Input */}
        <div className="flex-1 min-w-0">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Ask your question"
            rows={1}
            disabled={loading}
            className={cn(
              "w-full bg-transparent border-0 outline-none resize-none py-2 px-0",
              "text-sm text-text placeholder-text-muted",
              "focus:ring-0 focus:outline-none",
              "disabled:opacity-30 disabled:cursor-not-allowed",
              "scrollbar-hide"
            )}
            style={{ minHeight: "20px", maxHeight: "160px" }}
          />
        </div>

        {/* Send button */}
        <motion.button
          whileHover={canSend ? { scale: 1.02 } : undefined}
          whileTap={canSend ? { scale: 0.98 } : undefined}
          type="submit"
          disabled={!canSend}
          className={cn(
            "h-9 w-9 rounded-md flex items-center justify-center shrink-0 transition-all duration-200",
            canSend
              ? "bg-accent text-bg hover:bg-accent-hover"
              : "bg-white/[0.04] text-text-muted cursor-not-allowed"
          )}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <ArrowUp className="w-4 h-4" />
          )}
        </motion.button>
      </form>

      <p className="text-2xs text-text-muted text-center mt-2">
        Press Enter to send &middot; Shift + Enter for new line
      </p>
    </div>
  );
}