const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function sendMessage(message: string): Promise<{
  answer: string;
  sources: string[];
  confidence: number;
}> {
  try {
    const response = await fetch(`${API_URL}/api/v1/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error ${response.status}: ${errorText}`);
    }

    return response.json();
  } catch (error) {
    const msg = error instanceof Error ? error.message : "Unknown error";
    const urlHint = `${API_URL}/api/v1/chat`;
    throw new Error(`Failed to reach backend at ${urlHint}. ${msg}`);
  }
}
