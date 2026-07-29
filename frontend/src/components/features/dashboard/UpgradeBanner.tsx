"use client";

import { Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui";
import type { ToolInfo } from "@/lib/api";

export interface UpgradeBannerProps {
  tools: ToolInfo[];
}

/**
 * Banner shown when the user has locked paid tools, prompting an upgrade.
 * (No checkout flow yet — payment integration is deferred.)
 */
export function UpgradeBanner({ tools }: UpgradeBannerProps) {
  const lockedPaid = tools.filter((t) => t.is_paid && !t.hasAccess);
  if (lockedPaid.length === 0) return null;

  const planNames = Array.from(
    new Set(
      lockedPaid
        .map((t) => t.required_plan?.name)
        .filter((name): name is string => Boolean(name))
    )
  );

  return (
    <Card variant="glassStrong" className="border border-primary/30">
      <CardContent className="flex flex-col items-start gap-2 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-primary">
            <Sparkles className="h-5 w-5" />
          </span>
          <div>
            <p className="text-sm font-medium text-text-high">
              {lockedPaid.length} premium {lockedPaid.length === 1 ? "tool" : "tools"} locked
            </p>
            <p className="text-xs text-text-muted">
              {planNames.length > 0
                ? `Upgrade to ${planNames.join(" or ")} to unlock.`
                : "Upgrade your plan to unlock."}
            </p>
          </div>
        </div>
        <span className="text-xs text-text-muted">Plans &amp; billing coming soon</span>
      </CardContent>
    </Card>
  );
}

export default UpgradeBanner;
