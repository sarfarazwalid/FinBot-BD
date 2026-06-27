"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  User,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  FileText,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { cn, formatTimestamp, formatConfidence } from "@/lib/utils";
import { Message } from "@/types";

function ConfidenceBar({ confidence }: { confidence: number }) {
  const info = formatConfidence(confidence);
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 rounded-full bg-white/[0.04] overflow-hidden">
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

function SourceChip({ source, index }: { source: string; index: number }) {
  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.04 }}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-2xs font-medium transition-all duration-200 bg-white/[0.03] border border-divider text-text-secondary hover:text-text hover:bg-white/[0.05]"
    >
      <FileText className="w-3 h-3 text-accent/70" />
      <span className="truncate max-w-[120px]">{source}</span>
      <ExternalLink className="w-2.5 h-2.5 shrink-0 opacity-30" />
    </motion.button>
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
      // noop
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className={cn("flex gap-3 group", isUser ? "flex-row-reverse" : "")}
    >
      {/* Avatar */}
      <div className="shrink-0 mt-0.5">
        {isUser ? (
          <div className="w-8 h-8 rounded-md bg-card border border-border flex items-center justify-center">
            <User className="w-4 h-4 text-text-secondary" />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center text-bg font-bold text-sm">
            F
          </div>
        )}
      </div>

      {/* Content */}
      <div className={cn("flex flex-col max-w-[70%]", isUser ? "items-end" : "items-start")}>
        {/* Header */}
        <div className="flex items-center gap-2 mb-1.5 px-1">
          <span className="text-xs font-medium text-text">
            {isUser ? "You" : "FinBot BD"}
          </span>
          <span className="text-2xs text-text-muted">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        {/* Bubble */}
        <div
          className={cn(
            "relative px-4 py-3",
            isUser
              ? "bg-card border border-border rounded-lg rounded-tr-sm"
              : "bg-surface border border-border rounded-lg rounded-tl-sm"
          )}
        >
          {isUser ? (
            <p className="text-sm text-text whitespace-pre-wrap leading-relaxed">
              {message.content}
            </p>
          ) : (
            <div className="prose-custom text-sm max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Footer (assistant only) */}
        {!isUser && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className="flex flex-col w-full mt-2 gap-2"
          >
            {/* Actions */}
            <div className="flex items-center gap-1 px-1">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleCopy}
                className="h-7 w-7 rounded-md flex items-center justify-center text-text-muted hover:text-text hover:bg-white/[0.03] transition-all duration-200"
                title="Copy answer"
              >
                {copied ? (
                  <Check className="w-3.5 h-3.5 text-success" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setFeedback(feedback === "up" ? null : "up")}
                className={cn(
                  "h-7 w-7 rounded-md flex items-center justify-center transition-all duration-200",
                  feedback === "up"
                    ? "text-success bg-success/10"
                    : "text-text-muted hover:text-text hover:bg-white/[0.03]"
                )}
                title="Good response"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setFeedback(feedback === "down" ? null : "down")}
                className={cn(
                  "h-7 w-7 rounded-md flex items-center justify-center transition-all duration-200",
                  feedback === "down"
                    ? "text-danger bg-danger/10"
                    : "text-text-muted hover:text-text hover:bg-white/[0.03]"
                )}
                title="Bad response"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </motion.button>

              <div className="w-px h-4 bg-divider mx-1" />

              {message.sources && message.sources.length > 0 && (
                <button
                  onClick={() => setShowSources(!showSources)}
                  className="flex items-center gap-1 px-2 py-1 rounded-md text-2xs font-medium text-text-secondary hover:text-text hover:bg-white/[0.03] transition-all duration-200"
                >
                  <FileText className="w-3 h-3 text-accent/70" />
                  {message.sources.length} source{message.sources.length > 1 ? "s" : ""}
                  {showSources ? (
                    <ChevronUp className="w-3 h-3" />
                  ) : (
                    <ChevronDown className="w-3 h-3" />
                  )}
                </button>
              )}
            </div>

            {/* Sources */}
            {showSources && message.sources && message.sources.length > 0 && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                className="flex flex-wrap gap-1.5 overflow-hidden"
              >
                {message.sources.map((source, idx) => (
                  <SourceChip key={idx} source={source} index={idx} />
                ))}
              </motion.div>
            )}

            {/* Confidence */}
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