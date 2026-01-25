"use client";

import { Toaster as SonnerToaster } from "sonner";
export { toast } from "sonner";

export function Toaster() {
  return (
    <SonnerToaster
      position="top-right"
      toastOptions={{
        unstyled: true,
        classNames: {
          toast:
            "group toast bg-surface-800 border border-surface-700 text-text-high rounded-xl p-4 shadow-lg flex items-start gap-3 w-[356px]",
          title: "font-semibold text-sm",
          description: "text-text-muted text-sm mt-1",
          actionButton:
            "bg-primary hover:bg-primary-hover text-white text-sm font-medium px-3 py-1.5 rounded-lg transition-colors",
          cancelButton:
            "bg-surface-700 hover:bg-surface-600 text-text-high text-sm font-medium px-3 py-1.5 rounded-lg transition-colors",
          closeButton:
            "bg-surface-700 hover:bg-surface-600 text-text-muted rounded-lg p-1 transition-colors",
          success: "border-success/50",
          error: "border-danger/50",
          warning: "border-warning/50",
          info: "border-info/50",
          icon: "text-lg",
        },
      }}
      icons={{
        success: (
          <div className="w-5 h-5 rounded-full bg-success/20 flex items-center justify-center">
            <svg
              className="w-3 h-3 text-success"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={3}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        ),
        error: (
          <div className="w-5 h-5 rounded-full bg-danger/20 flex items-center justify-center">
            <svg
              className="w-3 h-3 text-danger"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={3}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        ),
        warning: (
          <div className="w-5 h-5 rounded-full bg-warning/20 flex items-center justify-center">
            <svg
              className="w-3 h-3 text-warning"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={3}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        ),
        info: (
          <div className="w-5 h-5 rounded-full bg-info/20 flex items-center justify-center">
            <svg
              className="w-3 h-3 text-info"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={3}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        ),
      }}
    />
  );
}
