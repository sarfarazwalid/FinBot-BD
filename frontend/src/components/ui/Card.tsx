"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
  onClick?: () => void;
}

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({
  children,
  className,
  hover = false,
  glow = false,
  onClick,
}: CardProps) {
  const Component = hover ? motion.div : "div";

  return (
    <Component
      {...(hover
        ? {
            whileHover: { y: -2 },
            transition: { type: "spring", stiffness: 300, damping: 20 },
          }
        : {})}
      onClick={onClick}
      className={cn(
        "glass-card rounded-2xl p-4",
        glow && "glow",
        hover && "cursor-pointer",
        onClick && "cursor-pointer",
        className
      )}
    >
      {children}
    </Component>
  );
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={cn("flex items-center gap-3 mb-3", className)}>
      {children}
    </div>
  );
}

export function CardContent({ children, className }: CardContentProps) {
  return <div className={cn("", className)}>{children}</div>;
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 mt-3 pt-3 border-t border-white/5",
        className
      )}
    >
      {children}
    </div>
  );
}