"use client";

import { motion } from "framer-motion";
import { User, Bot, Copy, Check, AlertCircle } from "lucide-react";
import { Message } from "@/types";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

function ConfidenceIndicator({ confidence }: { confidence: number }) {
  const color =
    confidence >= 0.7 ? "text-green-400" : confidence >= 0.4 ? "text-yellow-400" : "text-red-400";
  const label =
    confidence >= 0.7 ? "High" : confidence >= 0.4 ? "Medium" : "Low";

  return (
    <div className={`flex items-center gap-1.5 text-xs ${color}`}>
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75"></span>
        <span className="relative inline-flex rounded-full h-2 w-2 bg-current"></span>
      </span>
      {label} confidence
    </div>
  );
}

export function MessageBubble({ message }: { message: Message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm shrink-0 ${
          isUser ? "bg-secondary" : "bg-gradient-to-br from-primary to-accent"
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : "F"}
      </div>

      {/* Bubble */}
      <div className={`max-w-[80%] ${isUser ? "text-right" : ""}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser ? "bg-primary text-primary-foreground rounded-tr-sm" : "glass rounded-tl-sm"
          }`}
        >
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="text-sm prose prose-invert max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Assistant metadata */}
        {!isUser && (
          <div className="mt-2 flex flex-wrap items-center gap-3">
            {message.sources && message.sources.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {message.sources.map((source, idx) => (
                  <span
                    key={idx}
                    className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-muted-foreground"
                  >
                    {source}
                  </span>
                ))}
              </div>
            )}
            {typeof message.confidence === "number" && (
              <ConfidenceIndicator confidence={message.confidence} />
            )}
            <button
              onClick={handleCopy}
              className="text-muted-foreground hover:text-white transition-colors"
              title="Copy answer"
            >
              {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
}