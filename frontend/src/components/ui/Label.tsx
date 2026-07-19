"use client";

import { forwardRef, type LabelHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
}

const Label = forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, children, required, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn(
          "text-sm font-medium text-text-high",
          className
        )}
        {...props}
      >
        {children}
        {required && <span className="ml-1 text-danger">*</span>}
      </label>
    );
  }
);

Label.displayName = "Label";

export { Label };
