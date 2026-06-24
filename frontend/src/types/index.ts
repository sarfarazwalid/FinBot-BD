export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: string[];
  confidence?: number;
}

export interface ChatState {
  messages: Message[];
  loading: boolean;
  error: string | null;
}

export interface SendMessageResponse {
  answer: string;
  sources: string[];
  confidence: number;
}