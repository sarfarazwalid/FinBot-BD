"use client";

import { motion } from "framer-motion";
import {
  Sparkles,
  HelpCircle,
  Banknote,
  ShieldCheck,
  TrendingUp,
  Lock,
  RefreshCw,
  CreditCard,
  ArrowRight,
  MessageCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

const questions = [
  {
    category: "bKash",
    icon: Banknote,
    color: "text-pink-400",
    bg: "bg-pink-500/10",
    items: [
      "How do I reset my bKash PIN?",
      "What is the bKash cash-out charge?",
      "How to send money from bKash?",
    ],
  },
  {
    category: "Nagad",
    icon: CreditCard,
    color: "text-orange-400",
    bg: "bg-orange-500/10",
    items: [
      "How to open a Nagad account?",
      "Nagad cash-out fees and limits",
      "How to block my Nagad account?",
    ],
  },
  {
    category: "DBBL",
    icon: ShieldCheck,
    color: "text-blue-400",
    bg: "bg-blue-500/10",
    items: [
      "How to open a DBBL account?",
      "DBBL Nexus card benefits",
      "How to check DBBL balance?",
    ],
  },
  {
    category: "General",
    icon: HelpCircle,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    items: [
      "What banking services do you support?",
      "How secure is mobile banking?",
      "Compare bKash vs Nagad fees",
    ],
  },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const questionVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0 },
};

export function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-4"
    >
      {questions.map((section, idx) => (
        <motion.div
          key={section.category}
          variants={questionVariants}
          transition={{ delay: idx * 0.05 }}
        >
          <div className="flex items-center gap-2 mb-2.5 px-1">
            <div className={cn("w-5 h-5 rounded-lg flex items-center justify-center", section.bg)}>
              <section.icon className={cn("w-3 h-3", section.color)} />
            </div>
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              {section.category}
            </span>
          </div>
          <div className="grid gap-1.5">
            {section.items.map((question, qIdx) => (
              <motion.button
                key={question}
                whileHover={{ x: 4 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => onSelect(question)}
                className={cn(
                  "group flex items-center gap-3 w-full text-left px-3.5 py-2.5",
                  "rounded-xl text-xs transition-all duration-200",
                  "bg-white/[0.02] border border-white/[0.04]",
                  "hover:bg-white/[0.05] hover:border-white/10",
                  "text-muted-foreground hover:text-foreground"
                )}
              >
                <MessageCircle className="w-3.5 h-3.5 shrink-0 text-primary/60 group-hover:text-primary transition-colors duration-200" />
                <span className="flex-1 leading-relaxed">{question}</span>
                <ArrowRight className="w-3.5 h-3.5 shrink-0 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200" />
              </motion.button>
            ))}
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}