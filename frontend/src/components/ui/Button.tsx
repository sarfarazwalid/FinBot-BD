"use client";

import { forwardRef } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface ButtonProps {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  disabled?: boolean;
  className?: string;
  children?: React.ReactNode;
  type?: "button" | "submit" | "reset";
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      loading = false,
      disabled,
      children,
      type = "button",
      onClick,
    },
    ref
  ) => {
    const variants = {
      primary:
        "bg-accent text-[#16120E] font-semibold hover:bg-accent-hover shadow-button hover:shadow-button-hover disabled:shadow-none",
      secondary:
        "bg-transparent text-text border border-accent/30 hover:border-accent/60 hover:text-accent-hover disabled:border-border",
      ghost:
        "bg-transparent text-text-secondary hover:text-text hover:bg-white/[0.03] active:bg-white/[0.05]",
      danger:
        "bg-danger/10 text-danger border border-danger/20 hover:bg-danger/20 hover:border-danger/40",
    };

    const sizes = {
      sm: "h-8 px-3 text-xs gap-1.5 rounded-md",
      md: "h-10 px-4 text-sm gap-2 rounded-lg",
      lg: "h-12 px-6 text-base gap-2.5 rounded-lg",
    };

    const isDisabled = disabled || loading;

    return (
      <motion.button
        ref={(node) => {
          if (typeof ref === "function") ref(node);
          else if (ref) (ref as React.MutableRefObject<HTMLButtonElement | null>).current = node;
        }}
        whileHover={isDisabled ? undefined : { scale: 1.02 }}
        whileTap={isDisabled ? undefined : { scale: 0.98 }}
        type={type}
        disabled={isDisabled}
        onClick={onClick}
        className={cn(
          "relative inline-flex items-center justify-center font-medium transition-all duration-200",
          "focus-visible:outline-2 focus-visible:outline-accent/40 focus-visible:outline-offset-2",
          "disabled:opacity-30 disabled:cursor-not-allowed disabled:pointer-events-none",
          "select-none",
          variants[variant],
          sizes[size],
          className
        )}
      >
        {loading && <Loader2 className="w-4 h-4 animate-spin shrink-0" />}
        {children}
      </motion.button>
    );
  }
);

Button.displayName = "Button";

export { Button };
export type { ButtonProps };