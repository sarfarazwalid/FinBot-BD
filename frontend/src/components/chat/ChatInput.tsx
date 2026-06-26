"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Loader2,
  Sparkles,
  Mic,
  Paperclip,
  X,
  ArrowUp,
} from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  loading: boolean;
}

export function ChatInput({ onSend, loading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [focused, setFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
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
      {/* Gradient border glow */}
      <div
        className={cn(
          "absolute -inset-[1px] rounded-2xl opacity-0 transition-opacity duration-300",
          focused && "opacity-100"
        )}
        style={{
          background:
            "linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(6, 182, 212, 0.3))",
          filter: "blur(4px)",
        }}
      />

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
        className={cn(
          "relative flex items-end gap-2 p-2 rounded-2xl transition-all duration-300",
          "bg-surface-elevated/80 backdrop-blur-xl border",
          focused
            ? "border-primary/30 shadow-glow"
            : "border-border hover:border-white/20"
        )}
      >
        {/* Left controls */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            className="h-8 w-8 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200"
            title="Attach file"
          >
            <Paperclip className="w-4 h-4" />
          </button>
          <button
            type="button"
            className="h-8 w-8 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200"
            title="Voice input"
          >
            <Mic className="w-4 h-4" />
          </button>
        </div>

        {/* Input */}
        <div className="flex-1 min-w-0 relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Ask about bKash, Nagad, DBBL..."
            rows={1}
            disabled={loading}
            className={cn(
              "w-full bg-transparent border-0 outline-none resize-none py-2 px-0",
              "text-sm text-foreground placeholder-muted-foreground",
              "focus:ring-0 focus:outline-none",
              "disabled:opacity-40 disabled:cursor-not-allowed",
              "scrollbar-hide"
            )}
            style={{ minHeight: "20px", maxHeight: "160px" }}
          />
        </div>

        {/* Send button */}
        <motion.button
          whileHover={canSend ? { scale: 1.05 } : undefined}
          whileTap={canSend ? { scale: 0.95 } : undefined}
          type="submit"
          disabled={!canSend}
          className={cn(
            "h-9 w-9 rounded-xl flex items-center justify-center shrink-0 transition-all duration-200",
            canSend
              ? "bg-primary text-primary-foreground shadow-glow hover:bg-primary-hover"
              : "bg-white/5 text-muted-foreground cursor-not-allowed"
          )}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <ArrowUp className="w-4 h-4" />
          )}
        </motion.button>
      </form>

      {/* Bottom hint */}
      <AnimatePresence>
        {!focused && !input && !loading && (
          <motion.p
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            className="text-2xs text-muted-foreground/60 text-center mt-2"
          >
            Press Enter to send · Shift + Enter for new line
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}