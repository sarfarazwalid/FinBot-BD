"use client";

import { cn } from "@/lib/utils";

interface BadgeProps {
  variant?: "default" | "primary" | "success" | "warning" | "danger" | "info";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
  className?: string;
  dot?: boolean;
}

const variants = {
  default: "bg-white/5 text-muted-foreground border-white/10",
  primary: "bg-primary-muted text-emerald-300 border-primary/20",
  success: "bg-emerald-500/10 text-emerald-300 border-emerald-500/20",
  warning: "bg-warning-muted text-amber-300 border-warning/20",
  danger: "bg-rose-muted text-rose-300 border-rose/20",
  info: "bg-accent-muted text-cyan-300 border-accent/20",
};

const sizes = {
  sm: "text-2xs px-1.5 py-0.5 gap-1",
  md: "text-xs px-2 py-0.5 gap-1.5",
  lg: "text-sm px-2.5 py-1 gap-1.5",
};

export function Badge({
  variant = "default",
  size = "md",
  children,
  className,
  dot = false,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border font-medium",
        "transition-colors duration-200",
        variants[variant],
        sizes[size],
        className
      )}
    >
      {dot && (
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full",
            variant === "primary" && "bg-emerald-400",
            variant === "success" && "bg-emerald-400",
            variant === "warning" && "bg-amber-400",
            variant === "danger" && "bg-rose-400",
            variant === "info" && "bg-cyan-400",
            variant === "default" && "bg-muted-foreground"
          )}
        />
      )}
      {children}
    </span>
  );
}