"use client";

import { useCallback, useEffect, useState, useRef } from "react";
import { useConversations } from "./useConversations";
import { sendMessage } from "@/lib/api";
import { generateConversationTitle } from "@/lib/storage";
import { Message } from "./conversation.types";

/**
 * Module-level maps to avoid stale closure issues with async callbacks.
 */
const abortControllers = new Map<string, AbortController>();
const pendingRequestIds = new Map<string, string>();

export function useChat() {
  const {
    conversations,
    activeId,
    activeConversation,
    createConversation,
    setActiveConversation,
    clearActiveConversation,
    deleteConversation,
    addMessage,
    updateTitle,
    setConversationGenerating,
  } = useConversations();

  const loading = activeConversation?.isGenerating ?? false;
  const messages = activeConversation?.messages || [];

  // Per-conversation error state
  const errorMapRef = useRef<Map<string, string>>(new Map());
  const [displayedError, setDisplayedError] = useState<string | null>(null);

  useEffect(() => {
    if (activeId && errorMapRef.current.has(activeId)) {
      setDisplayedError(errorMapRef.current.get(activeId)!);
    } else {
      setDisplayedError(null);
    }
  }, [activeId]);

  const setConversationError = useCallback(
    (originatingId: string, message: string | null) => {
      if (message) {
        errorMapRef.current.set(originatingId, message);
        if (originatingId === activeId) setDisplayedError(message);
      } else {
        errorMapRef.current.delete(originatingId);
        if (originatingId === activeId) setDisplayedError(null);
      }
    },
    [activeId]
  );

  const deleteConversationWithAbort = useCallback(
    (id: string) => {
      abortControllers.get(id)?.abort();
      abortControllers.delete(id);
      pendingRequestIds.delete(id);
      errorMapRef.current.delete(id);
      deleteConversation(id);
    },
    [deleteConversation]
  );

  // Auto-title after first assistant response
  useEffect(() => {
    if (!activeConversation || !activeId) return;
    const msgs = activeConversation.messages;
    const lastMsg = msgs[msgs.length - 1];
    if (!lastMsg || lastMsg.role !== "assistant") return;
    if (activeConversation.title !== "New Conversation") return;
    const firstUserMsg = msgs.find((m) => m.role === "user");
    if (firstUserMsg) {
      updateTitle(activeId, generateConversationTitle(firstUserMsg.content));
    }
  }, [messages, activeId, activeConversation, updateTitle]);

  // send is NOT wrapped in useCallback. It's a regular function that
  // captures the latest values from the render. This avoids stale closure
  // issues entirely. React.memo optimization is not needed here since
  // send is passed as a prop only to ChatWindow and children.
  const send = async (content: string) => {
    setConversationError(activeId ?? "", null);

    const requestId = crypto.randomUUID();
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    // Capture originating conversationId BEFORE await
    let origId = activeConversation?.id;

    if (!origId) {
      // Create with userMessage AND isGenerating in one call
      const conv = createConversation({ requestId, userMessage });
      origId = conv.id;
    } else {
      addMessage(origId, userMessage);
      setConversationGenerating(origId, requestId, true);
    }

    // Register in module-level maps
    pendingRequestIds.set(origId, requestId);

    // Cancel any existing in-flight request
    abortControllers.get(origId)?.abort();
    const controller = new AbortController();
    abortControllers.set(origId, controller);

    try {
      const data = await sendMessage(content, controller.signal);

      // Stale response check (module level, never stale)
      if (pendingRequestIds.get(origId) !== requestId) return;

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
        timestamp: new Date(),
        sources: data.sources,
        confidence: data.confidence,
      };

      addMessage(origId, assistantMessage);
      setConversationGenerating(origId, requestId, false);
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      if (pendingRequestIds.get(origId) !== requestId) return;

      setConversationError(
        origId,
        err instanceof Error ? err.message : "Unknown error"
      );
      setConversationGenerating(origId, requestId, false);
    } finally {
      abortControllers.delete(origId);
      if (pendingRequestIds.get(origId) === requestId) {
        pendingRequestIds.delete(origId);
        setConversationGenerating(origId, requestId, false);
      }
    }
  };

  const clearChat = useCallback(() => {
    if (activeConversation && activeConversation.messages.length === 0) {
      deleteConversationWithAbort(activeConversation.id);
    }
    clearActiveConversation();
  }, [clearActiveConversation, deleteConversationWithAbort, activeConversation]);

  const goHome = useCallback(() => {
    if (activeConversation && activeConversation.messages.length === 0) {
      deleteConversationWithAbort(activeConversation.id);
    }
    clearActiveConversation();
  }, [clearActiveConversation, deleteConversationWithAbort, activeConversation]);

  return {
    messages,
    loading,
    error: displayedError,
    send,
    clearChat,
    goHome,
    activeId,
    activeConversation,
    setActiveConversation,
    conversations,
    createConversation,
    deleteConversation: deleteConversationWithAbort,
  };
}