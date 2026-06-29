"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare,
  Trash2,
  Search,
  Plus,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Conversation } from "@/hooks/conversation.types";
import { useConversations } from "@/hooks/useConversations";

const bankColors: Record<string, string> = {
  bKash: "bg-pink-500/10 text-pink-400 border-pink-500/20",
  Nagad: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  DBBL: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

function timeAgo(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days}d ago`;
  return new Date(timestamp).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

export function Sidebar({ onLogoClick, onNewConversation, onSelectConversation, onDeleteConversation, conversations: externalConversations, activeId: externalActiveId }: { onLogoClick?: () => void; onNewConversation?: () => void; onSelectConversation?: (id: string) => void; onDeleteConversation?: (id: string) => void; conversations?: Conversation[]; activeId?: string | null }) {
  const [expandedSection, setExpandedSection] = useState<string | null>("recent");
  const [searchQuery, setSearchQuery] = useState("");

  const hookData = useConversations();
  const conversations = externalConversations ?? hookData.conversations;
  const activeId = externalActiveId ?? hookData.activeId;
  const { createConversation, setActiveConversation, clearActiveConversation, deleteConversation: hookDelete } = hookData;
  const deleteConversation = onDeleteConversation ?? hookDelete;

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const today = conversations.filter((c) => {
    const diff = Date.now() - c.createdAt;
    return diff < 86400000;
  });

  const yesterday = conversations.filter((c) => {
    const diff = Date.now() - c.createdAt;
    return diff >= 86400000 && diff < 172800000;
  });

  const earlierThisWeek = conversations.filter((c) => {
    const diff = Date.now() - c.createdAt;
    return diff >= 172800000 && diff < 604800000;
  });

  const older = conversations.filter((c) => {
    const diff = Date.now() - c.createdAt;
    return diff >= 604800000;
  });

  const filteredConversations = conversations.filter((c) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      c.title.toLowerCase().includes(q) ||
      c.bank?.toLowerCase().includes(q) ||
      c.messages.some((m: { content: string }) => m.content.toLowerCase().includes(q))
    );
  });

  const renderConversationGroup = (items: typeof conversations, label?: string) => {
    if (items.length === 0) return null;
    return (
      <div className="mb-3">
        {label && (
          <div className="px-3 py-1.5 text-2xs font-medium text-text-muted uppercase tracking-wider">
            {label}
          </div>
        )}
        {items.map((conv) => (
          <motion.button
            key={conv.id}
            whileHover={{ x: 2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onSelectConversation ? onSelectConversation(conv.id) : setActiveConversation(conv.id)}
            className={cn(
              "w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs transition-all duration-200 group",
              conv.id === activeId
                ? "bg-card border-l-2 border-accent text-text"
                : "text-text-secondary hover:text-text hover:bg-white/[0.03]"
            )}
          >
            <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-50" />
            <span className="flex-1 truncate text-left">{conv.title || "New Chat"}</span>
            {conv.bank && (
              <span
                className={cn(
                  "text-2xs px-1.5 py-0.5 rounded-md border shrink-0",
                  bankColors[conv.bank] || "bg-white/5 text-text-muted border-divider"
                )}
              >
                {conv.bank}
              </span>
            )}
            <span className="text-2xs text-text-muted shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
              {timeAgo(conv.updatedAt)}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                deleteConversation(conv.id);
              }}
              className="shrink-0 w-5 h-5 rounded flex items-center justify-center opacity-0 group-hover:opacity-100 hover:text-danger transition-all duration-200"
              title="Delete conversation"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </motion.button>
        ))}
      </div>
    );
  };

  return (
    <motion.aside
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="w-[280px] h-full flex flex-col bg-surface border-r border-border"
    >
      {/* Brand Header — clickable to go home */}
      <div className="px-4 py-4 border-b border-divider">
        <button
          onClick={() => {
            clearActiveConversation();
            onLogoClick?.();
          }}
          className="flex items-center gap-2.5 w-full text-left"
        >
          <div className="w-8 h-8 rounded-md bg-accent flex items-center justify-center text-bg font-bold text-sm">
            F
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="font-heading font-semibold text-sm text-text tracking-tight truncate">
              FinBot BD
            </h1>
            <p className="text-2xs text-text-muted truncate">Banking Intelligence</p>
          </div>
        </button>
      </div>

      {/* New Conversation Button */}
      <div className="px-3 py-2">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => { if (onNewConversation) { onNewConversation(); } else { createConversation(); } }}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-text bg-accent/10 border border-accent/20 hover:bg-accent/15 hover:border-accent/30 transition-all duration-200"
        >
          <Plus className="w-4 h-4 text-accent" />
          New Conversation
        </motion.button>
      </div>

      {/* Search */}
      <div className="px-3 py-2">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-text-muted" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-8 pl-8 pr-3 rounded-md bg-card border border-border text-xs text-text placeholder-text-muted focus:outline-none focus:border-accent/40 transition-colors duration-200"
          />
        </div>
      </div>

      {/* Conversation List */}
      <nav className="flex-1 overflow-y-auto scrollbar-hide px-2 py-1">
        <button
          onClick={() => toggleSection("recent")}
          className="w-full flex items-center justify-between px-2 py-1.5 rounded-lg text-xs font-medium text-text-secondary hover:text-text hover:bg-white/[0.03] transition-all duration-200"
        >
          <span>Recent Conversations</span>
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
              {filteredConversations.length === 0 ? (
                <div className="px-3 py-4 text-xs text-text-muted text-center">
                  No conversations yet
                </div>
              ) : (
                <>
                  {renderConversationGroup(today, "Today")}
                  {renderConversationGroup(yesterday, "Yesterday")}
                  {renderConversationGroup(earlierThisWeek, "Earlier This Week")}
                  {renderConversationGroup(older, "Older")}
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-divider">
        <div className="flex items-center justify-between">
          <span className="text-2xs text-text-muted">Hybrid RAG</span>
          <span className="text-2xs text-text-muted">v1.0.0</span>
        </div>
      </div>
    </motion.aside>
  );
}