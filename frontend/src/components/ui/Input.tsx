"use client";

import { forwardRef } from "react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size"> {
  size?: "sm" | "md" | "lg";
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, size = "md", error, ...props }, ref) => {
    const sizes = {
      sm: "h-8 text-xs px-3",
      md: "h-9 text-sm px-3.5",
      lg: "h-11 text-base px-4",
    };

    return (
      <div className="relative w-full">
        <input
          ref={ref}
          className={cn(
            "w-full bg-surface-elevated border border-border rounded-xl",
            "text-foreground placeholder-muted-foreground",
            "transition-all duration-200 ease-out-quart",
            "focus:border-primary/50 focus:bg-white/[0.03] focus:shadow-glow focus:outline-none",
            "hover:border-white/20",
            "disabled:opacity-40 disabled:cursor-not-allowed",
            error && "border-rose/50 hover:border-rose focus:border-rose focus:shadow-glow-rose",
            sizes[size],
            className
          )}
          {...props}
        />
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-2xs text-rose mt-1.5 px-1"
          >
            {error}
          </motion.p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export { Input };
export type { InputProps };