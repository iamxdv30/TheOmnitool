"use client";

import { useMemo } from "react";
import { cn } from "@/lib/utils";

interface PasswordStrengthProps {
  password: string;
  className?: string;
}

interface StrengthLevel {
  label: string;
  color: string;
  barColor: string;
  segments: number;
}

const strengthLevels: StrengthLevel[] = [
  { label: "Too weak", color: "text-danger", barColor: "bg-danger", segments: 1 },
  { label: "Weak", color: "text-warning", barColor: "bg-warning", segments: 2 },
  { label: "Fair", color: "text-info", barColor: "bg-info", segments: 3 },
  { label: "Strong", color: "text-success", barColor: "bg-success", segments: 4 },
];

function calculateStrength(password: string): number {
  if (!password) return 0;

  let score = 0;

  // Length checks
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;

  // Character variety checks
  if (/[a-z]/.test(password)) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^a-zA-Z\d]/.test(password)) score++;

  // Cap at 4 (max strength level)
  return Math.min(Math.floor(score / 1.5), 4);
}

export function PasswordStrength({ password, className }: PasswordStrengthProps) {
  const strength = useMemo(() => calculateStrength(password), [password]);

  if (!password) return null;

  const level = strengthLevels[Math.max(0, strength - 1)] || strengthLevels[0];

  return (
    <div className={cn("space-y-1.5", className)}>
      {/* Strength bar */}
      <div className="flex gap-1">
        {[1, 2, 3, 4].map((segment) => (
          <div
            key={segment}
            className={cn(
              "h-1 flex-1 rounded-full transition-all duration-300",
              segment <= level.segments
                ? level.barColor
                : "bg-surface-700"
            )}
          />
        ))}
      </div>

      {/* Strength label */}
      <p className={cn("text-xs font-medium", level.color)}>
        Password strength: {level.label}
      </p>

      {/* Requirements checklist */}
      <ul className="text-xs text-text-muted space-y-0.5">
        <li className={cn(password.length >= 8 ? "text-success" : "")}>
          {password.length >= 8 ? "✓" : "○"} At least 8 characters
        </li>
        <li className={cn(/[A-Z]/.test(password) ? "text-success" : "")}>
          {/[A-Z]/.test(password) ? "✓" : "○"} One uppercase letter
        </li>
        <li className={cn(/[a-z]/.test(password) ? "text-success" : "")}>
          {/[a-z]/.test(password) ? "✓" : "○"} One lowercase letter
        </li>
        <li className={cn(/\d/.test(password) ? "text-success" : "")}>
          {/\d/.test(password) ? "✓" : "○"} One number
        </li>
      </ul>
    </div>
  );
}
