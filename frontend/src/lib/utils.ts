import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTimestamp(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);

  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (hours < 48) return "Yesterday";
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

export function formatConfidence(confidence: number): {
  label: string;
  color: string;
  barColor: string;
} {
  if (confidence >= 0.8)
    return {
      label: "High confidence",
      color: "text-emerald-400",
      barColor: "bg-emerald-400",
    };
  if (confidence >= 0.5)
    return {
      label: "Medium confidence",
      color: "text-amber-400",
      barColor: "bg-amber-400",
    };
  return {
    label: "Low confidence",
    color: "text-rose-400",
    barColor: "bg-rose-400",
  };
}