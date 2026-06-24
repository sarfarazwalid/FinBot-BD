"use client";

import { motion } from "framer-motion";
import { MessageSquare } from "lucide-react";

const SUGGESTIONS = [
  { label: "How to reset bKash PIN?", icon: "💳" },
  { label: "নগদ একাউন্ট ব্লক হলে কী করবো?", icon: "🔒" },
  { label: "DBBL card problem", icon: "🏦" },
];

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

export function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="grid gap-3">
      {SUGGESTIONS.map((suggestion, idx) => (
        <motion.button
          key={idx}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onSelect(suggestion.label)}
          className="glass glass-hover rounded-xl p-4 text-left flex items-center gap-3"
        >
          <span className="text-2xl">{suggestion.icon}</span>
          <div className="flex items-center gap-2 text-sm">
            <MessageSquare className="w-4 h-4 text-primary" />
            <span>{suggestion.label}</span>
          </div>
        </motion.button>
      ))}
    </div>
  );
}