"use client";

import { forwardRef, useRef, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface ButtonProps {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "outline";
  size?: "sm" | "md" | "lg" | "icon";
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
    const buttonRef = useRef<HTMLButtonElement | null>(null);

    const variants = {
      primary:
        "bg-primary text-primary-foreground hover:bg-primary-hover active:bg-primary-active shadow-glow hover:shadow-glow-md disabled:shadow-none",
      secondary:
        "bg-surface-elevated text-foreground hover:bg-white/10 active:bg-white/[0.08] border border-border disabled:border-transparent",
      ghost:
        "bg-transparent text-muted-foreground hover:text-foreground hover:bg-white/5 active:bg-white/[0.08]",
      danger:
        "bg-rose text-white hover:bg-rose-hover active:bg-rose/80 shadow-glow-rose hover:shadow-[0_0_30px_rgba(244,63,94,0.2)] disabled:shadow-none",
      outline:
        "bg-transparent text-foreground border border-border hover:border-primary/50 hover:text-primary active:bg-primary-muted",
    };

    const sizes = {
      sm: "h-8 px-3 text-xs gap-1.5 rounded-lg",
      md: "h-9 px-4 text-sm gap-2 rounded-xl",
      lg: "h-11 px-6 text-base gap-2.5 rounded-xl",
      icon: "h-9 w-9 rounded-xl",
    };

    const isDisabled = disabled || loading;

    return (
      <motion.button
        ref={(node) => {
          buttonRef.current = node;
          if (typeof ref === "function") ref(node);
          else if (ref) (ref as React.MutableRefObject<HTMLButtonElement | null>).current = node;
        }}
        whileHover={isDisabled ? undefined : { scale: 1.02 }}
        whileTap={isDisabled ? undefined : { scale: 0.98 }}
        type={type}
        disabled={isDisabled}
        onClick={onClick}
        className={cn(
          "relative inline-flex items-center justify-center font-medium transition-all duration-200 overflow-hidden",
          "focus-visible:outline-2 focus-visible:outline-primary/50 focus-visible:outline-offset-2",
          "disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-none",
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