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
      md: "h-10 text-sm px-4",
      lg: "h-12 text-base px-5",
    };

    return (
      <div className="relative w-full">
        <input
          ref={ref}
          className={cn(
            "w-full bg-card text-text placeholder-text-muted",
            "border border-border rounded-lg",
            "transition-all duration-200 ease-out",
            "focus:border-accent/50 focus:bg-card focus:outline-none",
            "hover:border-accent/30",
            "disabled:opacity-30 disabled:cursor-not-allowed",
            error && "border-danger/50 hover:border-danger focus:border-danger",
            sizes[size],
            className
          )}
          {...props}
        />
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -2 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-2xs text-danger mt-1.5 px-1"
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