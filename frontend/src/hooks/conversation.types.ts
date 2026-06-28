export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: string[];
  confidence?: number;
}

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
  /** Per-conversation flag: true while this conversation is awaiting an API response */
  isGenerating?: boolean;
  /** Unique ID of the last request sent from this conversation. Used to ignore stale responses. */
  pendingRequestId?: string;
}