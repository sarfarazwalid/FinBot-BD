"use client";

import { useState, useEffect, useCallback } from "react";

export interface Conversation {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  messages: Message[];
  language?: string;
  bank?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: string[];
  confidence?: number;
}

const STORAGE_KEY = "finbot_bd_conversations";
const ACTIVE_KEY = "finbot_bd_active_id";

function generateId(): string {
  return `conv_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

function loadFromStorage(): { conversations: Conversation[]; activeId: string | null } {
  if (typeof window === "undefined") {
    return { conversations: [], activeId: null };
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    const conversations: Conversation[] = stored ? JSON.parse(stored) : [];
    const activeId = localStorage.getItem(ACTIVE_KEY);
    return { conversations, activeId };
  } catch {
    return { conversations: [], activeId: null };
  }
}

function saveToStorage(conversations: Conversation[], activeId: string | null) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    if (activeId) {
      localStorage.setItem(ACTIVE_KEY, activeId);
    } else {
      localStorage.removeItem(ACTIVE_KEY);
    }
  } catch {
    // Storage full or unavailable
  }
}

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  // Load from storage on mount
  useEffect(() => {
    const { conversations: stored, activeId: storedActive } = loadFromStorage();
    if (stored.length > 0) {
      setConversations(
        stored.map((c) => ({
          ...c,
          messages: c.messages.map((m) => ({
            ...m,
            timestamp: new Date(m.timestamp),
          })),
        }))
      );
      setActiveId(storedActive);
    }
  }, []);

  // Save to storage on change
  useEffect(() => {
    saveToStorage(conversations, activeId);
  }, [conversations, activeId]);

  const getActiveConversation = useCallback(
    (): Conversation | null => {
      return conversations.find((c) => c.id === activeId) || null;
    },
    [conversations, activeId]
  );

  const createConversation = useCallback((): Conversation => {
    const newConv: Conversation = {
      id: generateId(),
      title: "",
      createdAt: Date.now(),
      updatedAt: Date.now(),
      messages: [],
      language: "en",
      bank: undefined,
    };

    setConversations((prev) => [newConv, ...prev]);
    setActiveId(newConv.id);
    return newConv;
  }, []);

  const deleteConversation = useCallback((id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    setActiveId((prev) => (prev === id ? null : prev));
  }, []);

  const updateConversation = useCallback(
    (id: string, updates: Partial<Conversation>) => {
      setConversations((prev) =>
        prev.map((c) =>
          c.id === id ? { ...c, ...updates, updatedAt: Date.now() } : c
        )
      );
    },
    []
  );

  const setActiveConversation = useCallback((id: string) => {
    setActiveId(id);
  }, []);

  const addMessage = useCallback(
    (conversationId: string, message: Message) => {
      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== conversationId) return c;

          const updated = {
            ...c,
            messages: [...c.messages, message],
            updatedAt: Date.now(),
          };

          // Auto-title from first user message
          if (c.messages.length === 0 && message.role === "user") {
            const title = message.content.slice(0, 40).trim();
            updated.title = title.length < message.content.length ? title + "…" : title;
          }

          return updated;
        })
      );
    },
    []
  );

  return {
    conversations,
    activeId,
    activeConversation: getActiveConversation(),
    createConversation,
    deleteConversation,
    updateConversation,
    setActiveConversation,
    addMessage,
  };
}