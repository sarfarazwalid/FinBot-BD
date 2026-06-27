"use client";

import { useCallback, useState, useEffect } from "react";
import { useConversations } from "./useConversations";
import { sendMessage } from "@/lib/api";
import { generateConversationTitle } from "@/lib/storage";

export function useChat() {
  const {
    activeId,
    activeConversation,
    createConversation,
    setActiveConversation,
    clearActiveConversation,
    addMessage,
    updateTitle,
  } = useConversations();

  const messages = activeConversation?.messages || [];
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-title after first assistant response
  useEffect(() => {
    if (!activeConversation || !activeId) return;
    const lastMsg = activeConversation.messages[activeConversation.messages.length - 1];
    if (!lastMsg || lastMsg.role !== "assistant") return;
    if (activeConversation.title !== "New Conversation") return;

    // Generate title from first user message using intelligent title generator
    const firstUserMsg = activeConversation.messages.find((m: { role: string }) => m.role === "user");
    if (firstUserMsg) {
      const title = generateConversationTitle(firstUserMsg.content);
      updateTitle(activeId, title);
    }
  }, [messages, activeId, activeConversation, updateTitle]);

  const send = useCallback(
    async (content: string) => {
      setLoading(true);
      setError(null);

      let conv = activeConversation;

      // Only create conversation on first message send
      if (!conv) {
        conv = createConversation();
      }

      const userMessage = {
        id: crypto.randomUUID(),
        role: "user" as const,
        content,
        timestamp: new Date(),
      };

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
    // Return to home — do NOT create new conversation
    clearActiveConversation();
  }, [clearActiveConversation]);

  const goHome = useCallback(() => {
    clearActiveConversation();
  }, [clearActiveConversation]);

  return {
    messages,
    loading,
    error,
    send,
    clearChat,
    goHome,
    activeId,
    setActiveConversation,
  };
}