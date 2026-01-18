"use client";

import { forwardRef, type TextareaHTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const textareaVariants = cva(
  // Base styles
  "w-full bg-surface-800 text-text-high placeholder:text-text-muted border transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-glow focus:ring-offset-2 focus:ring-offset-surface-900 disabled:cursor-not-allowed disabled:opacity-50 resize-none",
  {
    variants: {
      variant: {
        default: "border-surface-700 hover:border-primary/50",
        error: "border-danger focus:ring-danger",
        success: "border-success focus:ring-success",
      },
      textareaSize: {
        sm: "p-2 text-sm rounded-md min-h-[80px]",
        md: "p-3 text-base rounded-lg min-h-[120px]",
        lg: "p-4 text-lg rounded-lg min-h-[160px]",
      },
    },
    defaultVariants: {
      variant: "default",
      textareaSize: "md",
    },
  }
);

export interface TextareaProps
  extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "size">,
    VariantProps<typeof textareaVariants> {
  error?: string;
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, variant, textareaSize, error, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          textareaVariants({ variant: error ? "error" : variant, textareaSize }),
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);

Textarea.displayName = "Textarea";

export { Textarea, textareaVariants };
