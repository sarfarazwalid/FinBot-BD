"use client";

import { useCallback, useState } from "react";
import { useConversations } from "./useConversations";
import { sendMessage } from "@/lib/api";

export function useChat() {
  const {
    activeId,
    activeConversation,
    createConversation,
    setActiveConversation,
    addMessage,
  } = useConversations();

  const messages = activeConversation?.messages || [];
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = useCallback(
    async (content: string) => {
      setLoading(true);
      setError(null);

      let conv = activeConversation;

      // Create new conversation if none active
      if (!conv) {
        conv = createConversation();
      }

      const userMessage = {
        id: crypto.randomUUID(),
        role: "user" as const,
        content,
        timestamp: new Date(),
      };

      // Optimistically add user message
      addMessage(conv.id, userMessage);

      try {
        const data = await sendMessage(content);

        const assistantMessage = {
          id: crypto.randomUUID(),
          role: "assistant" as const,
          content: data.answer,
          timestamp: new Date(),
          sources: data.sources,
          confidence: data.confidence,
        };

        addMessage(conv.id, assistantMessage);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    },
    [activeConversation, createConversation, addMessage]
  );

  const clearChat = useCallback(() => {
    // Create fresh conversation (doesn't delete old ones)
    createConversation();
  }, [createConversation]);

  return {
    messages,
    loading,
    error,
    send,
    clearChat,
    activeId,
    conversations: [], // populated by useConversations
    setActiveConversation,
  };
}