"use client";

import { forwardRef, type HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { AlertCircle, CheckCircle, Info, XCircle } from "lucide-react";

const alertVariants = cva(
  "relative w-full rounded-lg border p-4 flex gap-3 items-start",
  {
    variants: {
      variant: {
        default: "bg-surface-800 border-surface-700 text-text-high",
        success: "bg-success/10 border-success text-success",
        warning: "bg-warning/10 border-warning text-warning",
        error: "bg-danger/10 border-danger text-danger",
        info: "bg-info/10 border-info text-info",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

const iconMap = {
  default: Info,
  success: CheckCircle,
  warning: AlertCircle,
  error: XCircle,
  info: Info,
};

export interface AlertProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {
  title?: string;
}

const Alert = forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = "default", title, children, ...props }, ref) => {
    const Icon = iconMap[variant || "default"];

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(alertVariants({ variant }), className)}
        {...props}
      >
        <Icon className="h-5 w-5 shrink-0" />
        <div className="flex-1">
          {title && (
            <h5 className="mb-1 font-medium leading-none tracking-tight">
              {title}
            </h5>
          )}
          <div className="text-sm opacity-90">{children}</div>
        </div>
      </div>
    );
  }
);

Alert.displayName = "Alert";

export { Alert, alertVariants };
