"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Menu, X } from "lucide-react";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { SuggestedQuestions } from "@/components/chat/SuggestedQuestions";
import { Sidebar } from "@/components/Sidebar";
import { useChat } from "@/hooks/useChat";

export default function Home() {
  const { messages, loading, error, send, clearChat } = useChat();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const hasMessages = messages.length > 0;

  const handleSuggestion = (question: string) => {
    send(question);
  };

  return (
    <main className="flex h-screen overflow-hidden bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden md:block">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
              className="fixed inset-0 bg-black/50 z-40 md:hidden"
            />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              className="fixed left-0 top-0 h-full z-50 md:hidden"
            >
              <Sidebar />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col relative">
        {/* Background effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl" />
        </div>

        {/* Mobile Header */}
        <div className="md:hidden flex items-center justify-between p-4 border-b border-white/10 relative z-10">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-lg glass"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            <span className="font-semibold">FinBot BD</span>
          </div>
          <div className="w-9" />
        </div>

        {/* Content */}
        <div className="flex-1 relative z-10">
          {!hasMessages ? (
            <div className="h-full flex flex-col items-center justify-center p-6">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="text-center mb-8"
              >
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-3xl mx-auto mb-4 shadow-lg shadow-primary/20">
                  F
                </div>
                <h1 className="text-2xl font-bold text-white mb-2">
                  Your intelligent banking assistant
                </h1>
                <p className="text-sm text-muted-foreground max-w-md">
                  Ask me anything about bKash, Nagad, or DBBL. I understand Bengali, English, and Banglish.
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="w-full max-w-lg"
              >
                <h3 className="text-xs font-medium text-muted-foreground mb-3 px-1">
                  Try asking
                </h3>
                <SuggestedQuestions onSelect={handleSuggestion} />
              </motion.div>
            </div>
          ) : (
            <ChatWindow
              messages={messages}
              loading={loading}
              error={error}
              onSend={send}
              onClear={clearChat}
            />
          )}
        </div>
      </div>
    </main>
  );
}