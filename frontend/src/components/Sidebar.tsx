"use client";

import { motion } from "framer-motion";
import { Banknote, CreditCard, Cpu, HelpCircle, RotateCcw } from "lucide-react";

export function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-72 h-full glass border-r border-white/10 flex flex-col p-6 gap-6"
    >
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-lg">
          F
        </div>
        <div>
          <h1 className="font-bold text-white tracking-tight">FinBot BD</h1>
          <p className="text-xs text-muted-foreground">Bangladesh Banking Assistant</p>
        </div>
      </div>

      {/* Supported Banks */}
      <section>
        <h3 className="text-xs font-medium text-muted-foreground mb-3">Supported Banks</h3>
        <div className="space-y-2">
          {[
            { name: "bKash", icon: <Banknote className="w-4 h-4" />, color: "text-pink-400" },
            { name: "Nagad", icon: <CreditCard className="w-4 h-4" />, color: "text-orange-400" },
            { name: "DBBL", icon: <Banknote className="w-4 h-4" />, color: "text-blue-400" },
          ].map((bank) => (
            <div key={bank.name} className="flex items-center gap-2.5 px-3 py-2 rounded-lg bg-white/5">
              <span className={bank.color}>{bank.icon}</span>
              <span className="text-sm font-medium">{bank.name}</span>
            </div>
          ))}
        </div>
      </section>

      {/* RAG Status */}
      <section>
        <h3 className="text-xs font-medium text-muted-foreground mb-3">RAG System Status</h3>
        <div className="space-y-2 px-3 py-2 rounded-lg bg-white/5">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-primary" /> Embeddings</span>
            <span className="flex items-center gap-1 text-green-400">
              <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75" /><span className="relative inline-flex rounded-full h-2 w-2 bg-current" /></span>
              Ready
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1.5"><Banknote className="w-3.5 h-3.5 text-primary" /> Pinecone</span>
            <span className="flex items-center gap-1 text-green-400">
              <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75" /><span className="relative inline-flex rounded-full h-2 w-2 bg-current" /></span>
              Ready
            </span>
          </div>
        </div>
      </section>

      {/* Quick questions */}
      <section className="flex-1 overflow-y-auto">
        <h3 className="text-xs font-medium text-muted-foreground mb-3">Quick Questions</h3>
        <div className="space-y-2">
          {[
            "How to reset PIN?",
            "Account blocked",
            "Cash out help",
          ].map((q) => (
            <button key={q} className="w-full text-left text-xs px-3 py-2 rounded-lg glass-hover flex items-center gap-2">
              <HelpCircle className="w-3.5 h-3.5 text-primary" />
              {q}
            </button>
          ))}
        </div>
      </section>

      {/* Footer */}
      <div className="text-[10px] text-muted-foreground mt-auto">
        FinBot BD v1.0.0 · Hybrid RAG
      </div>
    </motion.aside>
  );
}