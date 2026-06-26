"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  User,
  Bot,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Sparkles,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { cn, formatTimestamp, formatConfidence } from "@/lib/utils";
import { Message } from "@/types";

function ConfidenceBar({ confidence }: { confidence: number }) {
  const info = formatConfidence(confidence);
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 rounded-full bg-white/5 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${Math.round(confidence * 100)}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className={cn("h-full rounded-full", info.barColor)}
        />
      </div>
      <span className={cn("text-2xs font-medium shrink-0", info.color)}>
        {info.label}
      </span>
    </div>
  );
}

function SourceCard({ source, index }: { source: string; index: number }) {
  return (
    <motion.a
      href="#"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.05 }}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-2xs font-medium transition-all duration-200 bg-white/[0.03] border border-white/5 text-muted-foreground hover:text-foreground hover:bg-white/[0.06] hover:border-white/10"
    >
      <Sparkles className="w-3 h-3 text-primary" />
      <span className="truncate max-w-[120px]">{source}</span>
      <ExternalLink className="w-2.5 h-2.5 shrink-0 opacity-50" />
    </motion.a>
  );
}

export function MessageBubble({ message }: { message: Message }) {
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);
  const isUser = message.role === "user";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 16, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className={cn("flex gap-3 group", isUser ? "flex-row-reverse" : "")}
    >
      {/* Avatar */}
      <div className="shrink-0 mt-0.5">
        {isUser ? (
          <div className="w-8 h-8 rounded-xl bg-white/10 border border-white/10 flex items-center justify-center">
            <User className="w-4 h-4 text-muted-foreground" />
          </div>
        ) : (
          <div className="relative">
            <div className="w-8 h-8 rounded-xl bg-gradient-primary flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-primary/20">
              F
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-400 border-2 border-surface rounded-full" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className={cn("flex flex-col max-w-[75%]", isUser ? "items-end" : "items-start")}>
        {/* Header */}
        <div className="flex items-center gap-2 mb-1 px-1">
          <span className="text-xs font-medium text-foreground">
            {isUser ? "You" : "FinBot BD"}
          </span>
          <span className="text-2xs text-muted-foreground">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        {/* Bubble */}
        <div
          className={cn(
            "relative px-4 py-3",
            isUser
              ? "bg-primary/20 border border-primary/30 rounded-2xl rounded-tr-md"
              : "glass-strong rounded-2xl rounded-tl-md"
          )}
        >
          {isUser ? (
            <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
              {message.content}
            </p>
          ) : (
            <div className="prose-custom text-sm max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Footer actions (assistant only) */}
        {!isUser && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="flex flex-col w-full mt-2 gap-2"
          >
            {/* Action buttons */}
            <div className="flex items-center gap-1 px-1">
              {/* Copy */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleCopy}
                className="h-7 w-7 rounded-lg flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200"
                title="Copy answer"
              >
                {copied ? (
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </motion.button>

              {/* Thumbs up */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setFeedback(feedback === "up" ? null : "up")}
                className={cn(
                  "h-7 w-7 rounded-lg flex items-center justify-center transition-all duration-200",
                  feedback === "up"
                    ? "text-emerald-400 bg-emerald-400/10"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                )}
                title="Good response"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </motion.button>

              {/* Thumbs down */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setFeedback(feedback === "down" ? null : "down")}
                className={cn(
                  "h-7 w-7 rounded-lg flex items-center justify-center transition-all duration-200",
                  feedback === "down"
                    ? "text-rose-400 bg-rose-400/10"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                )}
                title="Bad response"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </motion.button>

              {/* Separator */}
              <div className="w-px h-4 bg-white/5 mx-1" />

              {/* Sources toggle */}
              {message.sources && message.sources.length > 0 && (
                <button
                  onClick={() => setShowSources(!showSources)}
                  className="flex items-center gap-1 px-2 py-1 rounded-lg text-2xs font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200"
                >
                  <Sparkles className="w-3 h-3" />
                  {message.sources.length} source{message.sources.length > 1 ? "s" : ""}
                  {showSources ? (
                    <ChevronUp className="w-3 h-3" />
                  ) : (
                    <ChevronDown className="w-3 h-3" />
                  )}
                </button>
              )}
            </div>

            {/* Sources dropdown */}
            {showSources && message.sources && message.sources.length > 0 && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="flex flex-wrap gap-1.5 overflow-hidden"
              >
                {message.sources.map((source, idx) => (
                  <SourceCard key={idx} source={source} index={idx} />
                ))}
              </motion.div>
            )}

            {/* Confidence bar */}
            {typeof message.confidence === "number" && (
              <div className="px-1">
                <ConfidenceBar confidence={message.confidence} />
              </div>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}