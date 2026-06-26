"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Banknote,
  CreditCard,
  HelpCircle,
  CircleDot,
  ChevronRight,
  MessageSquare,
  Trash2,
  ShieldCheck,
  TrendingUp,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";

const banks = [
  { name: "bKash", icon: Banknote, color: "text-pink-400", bg: "bg-pink-500/10" },
  { name: "Nagad", icon: CreditCard, color: "text-orange-400", bg: "bg-orange-500/10" },
  { name: "DBBL", icon: Banknote, color: "text-blue-400", bg: "bg-blue-500/10" },
];

const quickQuestions = [
  { label: "How to reset PIN?", icon: ShieldCheck },
  { label: "Account blocked", icon: HelpCircle },
  { label: "Cash out help", icon: TrendingUp },
  { label: "Transaction history", icon: Clock },
];

const recentChats = [
  { title: "bKash PIN reset guide", time: "2h ago" },
  { title: "Nagad cash out fees", time: "5h ago" },
  { title: "DBBL account opening", time: "1d ago" },
];

interface SidebarProps {
  className?: string;
  onClose?: () => void;
}

export function Sidebar({ className, onClose }: SidebarProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>("banks");
  const [selectedQuestion, setSelectedQuestion] = useState<string | null>(null);

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <motion.aside
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className={cn(
        "w-[280px] h-full flex flex-col",
        "bg-surface/80 backdrop-blur-2xl border-r border-border",
        className
      )}
    >
      {/* Brand Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-primary/20">
              F
            </div>
            <div className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-emerald-400 border-2 border-surface rounded-full" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="font-semibold text-sm text-foreground tracking-tight truncate">
              FinBot BD
            </h1>
            <p className="text-2xs text-muted-foreground truncate">
              Bangladesh Banking Assistant
            </p>
          </div>
        </div>
      </div>

      {/* RAG Status Bar */}
      <div className="px-4 py-3 border-b border-border">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-glow border border-primary/10">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400" />
          </span>
          <span className="text-xs font-medium text-emerald-400">RAG System Ready</span>
          <span className="ml-auto text-2xs text-muted-foreground">Hybrid</span>
        </div>
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 overflow-y-auto scroll-area py-2 px-2 space-y-0.5">
        {/* New Chat */}
        <button
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-foreground bg-primary-muted border border-primary/20 hover:bg-primary/15 transition-all duration-200"
        >
          <MessageSquare className="w-4 h-4 text-primary" />
          New conversation
        </button>

        <div className="my-2 border-t border-border" />

        {/* Supported Banks */}
        <div>
          <button
            onClick={() => toggleSection("banks")}
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200"
          >
            <span className="flex items-center gap-2">
              <Banknote className="w-3.5 h-3.5" />
              Supported Banks
            </span>
            <ChevronRight
              className={cn(
                "w-3.5 h-3.5 transition-transform duration-200",
                expandedSection === "banks" && "rotate-90"
              )}
            />
          </button>
          <AnimatePresence>
            {expandedSection === "banks" && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="overflow-hidden"
              >
                <div className="px-2 py-1 space-y-1">
                  {banks.map((bank) => (
                    <div
                      key={bank.name}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2 rounded-lg border transition-all duration-200",
                        "border-transparent hover:border-white/5 hover:bg-white/[0.02]"
                      )}
                    >
                      <div className={cn("w-7 h-7 rounded-lg flex items-center justify-center", bank.bg)}>
                        <bank.icon className={cn("w-3.5 h-3.5", bank.color)} />
                      </div>
                      <span className="text-sm font-medium text-foreground">{bank.name}</span>
                      <CircleDot className="w-2.5 h-2.5 text-emerald-400 ml-auto" />
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Quick Questions */}
        <div>
          <button
            onClick={() => toggleSection("questions")}
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200"
          >
            <span className="flex items-center gap-2">
              <HelpCircle className="w-3.5 h-3.5" />
              Quick Questions
            </span>
            <ChevronRight
              className={cn(
                "w-3.5 h-3.5 transition-transform duration-200",
                expandedSection === "questions" && "rotate-90"
              )}
            />
          </button>
          <AnimatePresence>
            {expandedSection === "questions" && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="overflow-hidden"
              >
                <div className="px-2 py-1 space-y-1">
                  {quickQuestions.map((q) => (
                    <button
                      key={q.label}
                      onClick={() => setSelectedQuestion(q.label)}
                      className={cn(
                        "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs transition-all duration-200",
                        "text-muted-foreground hover:text-foreground hover:bg-white/5"
                      )}
                    >
                      <q.icon className="w-3.5 h-3.5 text-primary shrink-0" />
                      <span className="truncate">{q.label}</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Recent Chats */}
        <div>
          <button
            onClick={() => toggleSection("recent")}
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all duration-200"
          >
            <span className="flex items-center gap-2">
              <Clock className="w-3.5 h-3.5" />
              Recent Chats
            </span>
            <ChevronRight
              className={cn(
                "w-3.5 h-3.5 transition-transform duration-200",
                expandedSection === "recent" && "rotate-90"
              )}
            />
          </button>
          <AnimatePresence>
            {expandedSection === "recent" && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="overflow-hidden"
              >
                <div className="px-2 py-1 space-y-1">
                  {recentChats.map((chat) => (
                    <button
                      key={chat.title}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs transition-all duration-200 text-muted-foreground hover:text-foreground hover:bg-white/5"
                    >
                      <MessageSquare className="w-3.5 h-3.5 shrink-0" />
                      <span className="truncate flex-1 text-left">{chat.title}</span>
                      <span className="text-2xs text-muted-foreground shrink-0">{chat.time}</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="flex -space-x-1">
              <div className="w-5 h-5 rounded-full bg-gradient-primary flex items-center justify-center text-[8px] font-bold text-white ring-2 ring-surface">
                F
              </div>
              <div className="w-5 h-5 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-[8px] font-bold text-white ring-2 ring-surface">
                AI
              </div>
            </div>
            <span className="text-xs text-muted-foreground">Hybrid RAG</span>
          </div>
          <span className="text-2xs text-muted-foreground">v1.0.0</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 text-2xs text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            All systems operational
          </span>
        </div>
      </div>
    </motion.aside>
  );
}