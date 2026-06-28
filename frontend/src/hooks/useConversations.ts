"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { storage, generateConversationTitle, STORAGE_KEY, ACTIVE_KEY } from "@/lib/storage";
import { Conversation, Message } from "./conversation.types";

// Re-export for backward compatibility
export type { Conversation, Message };

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  // Load from storage on mount
  useEffect(() => {
    storage.loadConversations().then((loaded) => {
      setConversations(loaded);
    });
    storage.loadActiveId().then(setActiveId);
  }, []);

  const getActiveConversation = useCallback((): Conversation | null => {
    return conversations.find((c) => c.id === activeId) || null;
  }, [conversations, activeId]);

  const createConversation = useCallback(
    (initialGenerating?: { requestId: string; userMessage: Message }): Conversation => {
      const newConv: Conversation = {
        id: crypto.randomUUID(),
        title: "New Conversation",
        createdAt: Date.now(),
        updatedAt: Date.now(),
        messages: initialGenerating ? [initialGenerating.userMessage] : [],
        language: "en",
        bank: undefined,
        isGenerating: initialGenerating ? true : undefined,
        pendingRequestId: initialGenerating ? initialGenerating.requestId : undefined,
      };

      // Read fresh from storage to avoid stale closure issues
      let latestConversations: Conversation[] = [];
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        latestConversations = stored ? JSON.parse(stored) : [];
      } catch {
        latestConversations = [];
      }

      // Atomically remove empty active conversation (if any)
      const filtered = latestConversations.filter(
        (c) => c.id !== activeId || c.messages.length > 0
      );
      const next = [newConv, ...filtered];

      // Use a function updater for reliability with React 18 batching
      setConversations(() => next);
      setActiveId(newConv.id);

      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        // Storage full
      }
      localStorage.setItem(ACTIVE_KEY, newConv.id);

      if (activeId) {
        storage.clearDraft(activeId);
      }

      return newConv;
    },
    [activeId]
  );

  const deleteConversation = useCallback((id: string) => {
    setConversations((prev) => {
      const updated = prev.filter((c) => c.id !== id);
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch {
        // Storage full
      }
      return updated;
    });
    setActiveId((prev) => {
      if (prev === id) {
        localStorage.removeItem(ACTIVE_KEY);
        return null;
      }
      return prev;
    });
    storage.clearDraft(id);
  }, []);

  const updateConversation = useCallback(
    (id: string, updates: Partial<Conversation>) => {
      setConversations((prev) => {
        const updated = prev.map((c) =>
          c.id === id ? { ...c, ...updates, updatedAt: Date.now() } : c
        );
        // Re-sort: pinned first, then by updatedAt DESC
        updated.sort((a, b) => {
          if (a.pinned && !b.pinned) return -1;
          if (!a.pinned && b.pinned) return 1;
          return b.updatedAt - a.updatedAt;
        });
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
        } catch {
          // Storage full
        }
        return updated;
      });
    },
    []
  );

  const setActiveConversation = useCallback((id: string) => {
    setActiveId(id);
    localStorage.setItem(ACTIVE_KEY, id);
  }, []);

  const clearActiveConversation = useCallback(() => {
    setActiveId(null);
    localStorage.removeItem(ACTIVE_KEY);
  }, []);

  const addMessage = useCallback((conversationId: string, message: Message) => {
    setConversations((prev) => {
      const updated = prev.map((c) => {
        if (c.id !== conversationId) return c;
        return {
          ...c,
          messages: [...c.messages, message],
          updatedAt: Date.now(),
        };
      });
      // Re-sort
      updated.sort((a, b) => {
        if (a.pinned && !b.pinned) return -1;
        if (!a.pinned && b.pinned) return 1;
        return b.updatedAt - a.updatedAt;
      });
      try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
        } catch {
          // Storage full
        }
      return updated;
    });
  }, []);

  const updateTitle = useCallback((conversationId: string, title: string) => {
    updateConversation(conversationId, { title });
  }, [updateConversation]);

  const pinConversation = useCallback((id: string) => {
    updateConversation(id, { pinned: true });
  }, [updateConversation]);

  const unpinConversation = useCallback((id: string) => {
    updateConversation(id, { pinned: false });
  }, [updateConversation]);

  const archiveConversation = useCallback((id: string) => {
    updateConversation(id, { archived: true });
    if (activeId === id) {
      clearActiveConversation();
    }
  }, [updateConversation, activeId, clearActiveConversation]);

  const unarchiveConversation = useCallback((id: string) => {
    updateConversation(id, { archived: false });
  }, [updateConversation]);

  const setConversationGenerating = useCallback(
    (id: string, requestId: string, isGenerating: boolean) => {
      setConversations((prev) => {
        const updated = prev.map((c) => {
          if (c.id !== id) return c;
          return {
            ...c,
            isGenerating,
            pendingRequestId: isGenerating ? requestId : undefined,
            updatedAt: Date.now(),
          };
        });
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
        } catch {
          // Storage full
        }
        return updated;
      });
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
    clearActiveConversation,
    addMessage,
    updateTitle,
    pinConversation,
    unpinConversation,
    archiveConversation,
    unarchiveConversation,
    setConversationGenerating,
  };
}