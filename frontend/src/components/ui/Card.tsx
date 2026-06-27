"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
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

export function Card({ children, className, hover = false, onClick }: CardProps) {
  const Component = hover ? motion.div : "div";

  return (
    <Component
      {...(hover ? { whileHover: { y: -2 }, transition: { duration: 0.2 } } : {})}
      onClick={onClick}
      className={cn(
        "panel-elevated p-5",
        hover && "panel-hover cursor-pointer",
        onClick && "cursor-pointer",
        className
      )}
    >
      {children}
    </Component>
  );
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return <div className={cn("flex items-center gap-3 mb-4", className)}>{children}</div>;
}

export function CardContent({ children, className }: CardContentProps) {
  return <div className={cn("", className)}>{children}</div>;
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div className={cn("flex items-center gap-2 mt-4 pt-4 border-t border-divider", className)}>
      {children}
    </div>
  );
}