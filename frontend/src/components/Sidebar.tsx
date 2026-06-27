"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Banknote,
  CreditCard,
  HelpCircle,
  ChevronRight,
  MessageSquare,
  ShieldCheck,
  TrendingUp,
  Clock,
  Building2,
  FileText,
  Search,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const banks = [
  { name: "bKash", icon: Banknote },
  { name: "Nagad", icon: CreditCard },
  { name: "DBBL", icon: Building2 },
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

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <motion.aside
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={cn(
        "w-[280px] h-full flex flex-col bg-surface border-r border-border",
        className
      )}
    >
      {/* Brand Header */}
      <div className="px-5 py-5 border-b border-divider">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center text-bg font-bold text-base font-heading">
            F
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="font-heading font-semibold text-sm text-text tracking-tight truncate">
              FinBot BD
            </h1>
            <p className="text-2xs text-text-secondary truncate mt-0.5">
              Banking Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="px-4 py-3 border-b border-divider">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-card border border-border">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-60" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-success" />
          </span>
          <span className="text-xs font-medium text-text-secondary">RAG System</span>
          <span className="ml-auto text-xs text-success">Operational</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto scrollbar-hide py-3 px-3 space-y-1">
        {/* New Chat */}
        <button className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-text bg-accent/10 border border-accent/20 hover:bg-accent/15 transition-all duration-200">
          <MessageSquare className="w-4 h-4 text-accent" />
          New conversation
        </button>

        <div className="my-3 border-t border-divider" />

        {/* Supported Banks */}
        <div>
          <button
            onClick={() => toggleSection("banks")}
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium text-text-secondary hover:text-text hover:bg-white/[0.03] transition-all duration-200"
          >
            <span className="flex items-center gap-2">
              <Building2 className="w-3.5 h-3.5" />
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
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-2 py-1 space-y-0.5">
                  {banks.map((bank) => (
                    <div
                      key={bank.name}
                      className="flex items-center gap-3 px-3 py-2 rounded-lg text-text-secondary hover:text-text hover:bg-white/[0.02] transition-all duration-200"
                    >
                      <bank.icon className="w-3.5 h-3.5 text-accent/70" />
                      <span className="text-xs font-medium">{bank.name}</span>
                      <span className="w-1.5 h-1.5 rounded-full bg-success ml-auto" />
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
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium text-text-secondary hover:text-text hover:bg-white/[0.03] transition-all duration-200"
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
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-2 py-1 space-y-0.5">
                  {quickQuestions.map((q) => (
                    <button
                      key={q.label}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs text-text-secondary hover:text-text hover:bg-white/[0.02] transition-all duration-200"
                    >
                      <q.icon className="w-3.5 h-3.5 text-accent/70 shrink-0" />
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
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium text-text-secondary hover:text-text hover:bg-white/[0.03] transition-all duration-200"
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
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="px-2 py-1 space-y-0.5">
                  {recentChats.map((chat) => (
                    <button
                      key={chat.title}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs text-text-secondary hover:text-text hover:bg-white/[0.02] transition-all duration-200"
                    >
                      <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-50" />
                      <span className="truncate flex-1 text-left">{chat.title}</span>
                      <span className="text-2xs text-text-muted shrink-0">{chat.time}</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-divider">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-accent/10 border border-accent/20 flex items-center justify-center">
              <FileText className="w-3 h-3 text-accent" />
            </div>
            <span className="text-xs text-text-secondary">Hybrid RAG</span>
          </div>
          <span className="text-2xs text-text-muted">v1.0.0</span>
        </div>
      </div>
    </motion.aside>
  );
}