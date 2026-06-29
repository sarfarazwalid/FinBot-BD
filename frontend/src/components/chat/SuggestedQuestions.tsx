"use client";

import { motion } from "framer-motion";
import {
  Banknote,
  CreditCard,
  Building2,
  ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

interface PromptCard {
  bank: string;
  icon: typeof Banknote;
  prompts: {
    flag: string;
    text: string;
  }[];
}

const prompts: PromptCard[] = [
  {
    bank: "bKash",
    icon: Banknote,
    prompts: [
      { flag: "🇬🇧", text: "How do I reset my bKash PIN?" },
      { flag: "🇧🇩", text: "আমি কীভাবে bKash PIN রিসেট করব?" },
      { flag: "🗣️", text: "bKash PIN kivabe reset korbo?" },
    ],
  },
  {
    bank: "Nagad",
    icon: Banknote,
    prompts: [
      { flag: "🇬🇧", text: "How do I reset my Nagad PIN?" },
      { flag: "🇧🇩", text: "আমি কীভাবে Nagad PIN রিসেট করব?" },
      { flag: "🗣️", text: "Nagad PIN kivabe reset korbo?" },
    ],
  },
  {
    bank: "DBBL",
    icon: Building2,
    prompts: [
      { flag: "🇬🇧", text: "How do I reset my DBBL PIN?" },
      { flag: "🇧🇩", text: "আমি কীভাবে DBBL PIN রিসেট করব?" },
      { flag: "🗣️", text: "DBBL PIN kivabe reset korbo?" },
    ],
  },
];

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.35,
      ease: [0.22, 1, 0.36, 1],
    },
  }),
};

const buttonVariants = {
  hidden: { opacity: 0, x: -8 },
  visible: (i: number) => ({
    opacity: 1,
    x: 0,
    transition: {
      delay: i * 0.06 + 0.25,
      duration: 0.2,
      ease: [0.22, 1, 0.36, 1],
    },
  }),
};

export function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="w-full">
      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {prompts.map((card, cardIdx) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={card.bank}
              custom={cardIdx}
              variants={cardVariants}
              initial="hidden"
              animate="visible"
              whileHover={{
                y: -2,
                transition: { duration: 0.2, ease: [0.22, 1, 0.36, 1] },
              }}
              className={cn(
                "panel-elevated p-6 flex flex-col gap-4",
                "hover:bg-card-hover hover:border-accent/25 hover:shadow-card-hover",
                "transition-all duration-200"
              )}
            >
              {/* Bank Header */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-md bg-card border border-border flex items-center justify-center">
                  <Icon className="w-4 h-4 text-accent/80" />
                </div>
                <div>
                  <span className="text-sm font-medium text-text">{card.bank}</span>
                  <p className="text-2xs text-text-muted mt-0.5">PIN Reset</p>
                </div>
              </div>

              <div className="border-t border-divider" />

              {/* Prompt Buttons */}
              <div className="flex flex-col gap-2.5">
                {card.prompts.map((prompt, pIdx) => (
                  <motion.button
                    key={prompt.text}
                    custom={pIdx}
                    variants={buttonVariants}
                    initial="hidden"
                    animate="visible"
                    whileHover={{
                      y: -1,
                      scale: 1.01,
                      transition: { duration: 0.15, ease: [0.22, 1, 0.36, 1] },
                    }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => onSelect(prompt.text)}
                    className={cn(
                      "group flex items-start gap-2.5 w-full text-left px-3.5 py-2.5",
                      "rounded-md text-xs transition-all duration-200",
                      "bg-white/[0.02] border border-divider",
                      "hover:bg-white/[0.04] hover:border-accent/30 hover:shadow-sm",
                      "text-text-secondary hover:text-text"
                    )}
                  >
                    <span className="text-xs shrink-0 mt-0.5 leading-none">
                      {prompt.flag}
                    </span>
                    <span className="flex-1 leading-relaxed">{prompt.text}</span>
                    <ArrowRight className="w-3 h-3 shrink-0 opacity-0 -translate-x-1 group-hover:opacity-60 group-hover:translate-x-0 transition-all duration-200 mt-0.5" />
                  </motion.button>
                ))}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Scroll hint — mobile only */}
      <div className="md:hidden flex justify-center mt-4">
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-white/[0.02] border border-divider">
          <div className="flex gap-1">
            <span className="block w-1 h-1 rounded-full bg-text-muted animate-pulse-subtle" />
            <span className="block w-1 h-1 rounded-full bg-text-muted animate-pulse-subtle" style={{ animationDelay: "0.3s" }} />
            <span className="block w-1 h-1 rounded-full bg-text-muted animate-pulse-subtle" style={{ animationDelay: "0.6s" }} />
          </div>
          <span className="text-2xs text-text-muted">Swipe to explore</span>
        </div>
      </div>
    </div>
  );
}