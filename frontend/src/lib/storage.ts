"use client";

export interface Conversation {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  messages: Message[];
  language?: string;
  bank?: string;
  pinned?: boolean;
  archived?: boolean;
  preview?: string;
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
const SIDEBAR_SCROLL_KEY = "finbot_bd_sidebar_scroll";
const DRAFTS_KEY = "finbot_bd_drafts";

function generateId(): string {
  return `conv_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export interface ConversationStorage {
  loadConversations(): Promise<Conversation[]>;
  saveConversations(conversations: Conversation[]): Promise<void>;
  loadActiveId(): Promise<string | null>;
  saveActiveId(id: string | null): Promise<void>;
  loadScrollPosition(): Promise<number>;
  saveScrollPosition(position: number): Promise<void>;
  loadDraft(conversationId: string): Promise<string>;
  saveDraft(conversationId: string, draft: string): Promise<void>;
  clearDraft(conversationId: string): Promise<void>;
}

export class LocalStorageRepository implements ConversationStorage {
  async loadConversations(): Promise<Conversation[]> {
    if (typeof window === "undefined") return [];
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      const conversations: Conversation[] = stored ? JSON.parse(stored) : [];
      conversations.sort((a, b) => b.updatedAt - a.updatedAt);
      return conversations;
    } catch {
      return [];
    }
  }

  async saveConversations(conversations: Conversation[]): Promise<void> {
    if (typeof window === "undefined") return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
    } catch {
      // Storage full
    }
  }

  async loadActiveId(): Promise<string | null> {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(ACTIVE_KEY);
  }

  async saveActiveId(id: string | null): Promise<void> {
    if (typeof window === "undefined") return;
    if (id) {
      localStorage.setItem(ACTIVE_KEY, id);
    } else {
      localStorage.removeItem(ACTIVE_KEY);
    }
  }

  async loadScrollPosition(): Promise<number> {
    if (typeof window === "undefined") return 0;
    const stored = localStorage.getItem(SIDEBAR_SCROLL_KEY);
    return stored ? parseInt(stored, 10) : 0;
  }

  async saveScrollPosition(position: number): Promise<void> {
    if (typeof window === "undefined") return;
    localStorage.setItem(SIDEBAR_SCROLL_KEY, position.toString());
  }

  async loadDraft(conversationId: string): Promise<string> {
    if (typeof window === "undefined") return "";
    const drafts = await this.loadAllDrafts();
    return drafts[conversationId] || "";
  }

  async saveDraft(conversationId: string, draft: string): Promise<void> {
    if (typeof window === "undefined") return;
    const drafts = await this.loadAllDrafts();
    drafts[conversationId] = draft;
    localStorage.setItem(DRAFTS_KEY, JSON.stringify(drafts));
  }

  async clearDraft(conversationId: string): Promise<void> {
    if (typeof window === "undefined") return;
    const drafts = await this.loadAllDrafts();
    delete drafts[conversationId];
    localStorage.setItem(DRAFTS_KEY, JSON.stringify(drafts));
  }

  private async loadAllDrafts(): Promise<Record<string, string>> {
    if (typeof window === "undefined") return {};
    try {
      const stored = localStorage.getItem(DRAFTS_KEY);
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  }
}

// Singleton instance
export const storage = new LocalStorageRepository();

// Helper to generate intelligent title
export function generateConversationTitle(firstMessage: string): string {
  const text = firstMessage.trim();
  
  // Detect bank
  const banks = ["bKash", "Nagad", "DBBL", "Rocket", "Upay"];
  let detectedBank = "";
  for (const bank of banks) {
    if (text.toLowerCase().includes(bank.toLowerCase())) {
      detectedBank = bank;
      break;
    }
  }

  // Detect intent patterns
  const intents: Record<string, string> = {
    "pin|PIN|reset": "PIN Reset",
    "cash out|cashout": "Cash Out",
    "transfer|send money": "Transfer",
    "balance|check balance": "Balance Check",
    "account|create account|open": "Account",
    "card|atm": "ATM Card",
    "loan": "Loan",
    "bill|pay bill": "Bill Payment",
    "recharge|topup|top up": "Recharge",
    "limit|transaction limit": "Transaction Limit",
    "password|forgot password": "Password",
  };

  let detectedIntent = "";
  for (const [pattern, intent] of Object.entries(intents)) {
    const regex = new RegExp(pattern, "i");
    if (regex.test(text)) {
      detectedIntent = intent;
      break;
    }
  }

  // Build title
  if (detectedBank && detectedIntent) {
    return `${detectedIntent} ${detectedBank}`;
  } else if (detectedBank) {
    return `${detectedBank} Inquiry`;
  } else {
    // Fallback: first 40 chars, cleaned up
    const cleaned = text.replace(/[?!.,;:]+$/, "").trim();
    return cleaned.length > 40 ? cleaned.slice(0, 37) + "…" : cleaned;
  }
}