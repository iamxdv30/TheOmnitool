"use client";

import Link from "next/link";
import { ExternalLink } from "lucide-react";
import { Card } from "@/components/ui";
import type { UsageHistoryEntry } from "@/types";
import { getToolIcon, getToolRoute } from "./toolMaps";

export interface UsageHistoryProps {
  history: UsageHistoryEntry[];
  totalCount: number;
  isLoading?: boolean;
}

function formatTimestamp(timestamp: string | null): string {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return "";

  const diffMs = Date.now() - date.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

/**
 * "Usage & History" card: total usage count plus recent activity list.
 */
export function UsageHistory({ history, totalCount, isLoading }: UsageHistoryProps) {
  return (
    <Card variant="glass" padding="lg" className="w-full max-w-md rounded-2xl">
      <div className="flex items-baseline justify-between">
        <h3 className="font-display text-lg font-bold text-text-high">
          Usage &amp; History
        </h3>
        <span className="flex items-baseline gap-1.5">
          <span className="font-display text-2xl font-bold text-secondary">
            {totalCount}
          </span>
          <span className="text-[10px] font-semibold uppercase tracking-wider text-text-muted">
            Tools used
          </span>
        </span>
      </div>

      <p className="mt-4 text-[10px] font-semibold uppercase tracking-widest text-text-muted">
        Recent activity
      </p>

      {isLoading ? (
        <p className="py-4 text-center text-sm text-text-muted">Loading…</p>
      ) : history.length === 0 ? (
        <p className="py-4 text-center text-sm text-text-muted">
          No activity yet — launch a tool to get started.
        </p>
      ) : (
        <ul className="mt-2 space-y-2">
          {history.map((entry, index) => {
            const Icon = getToolIcon(null, entry.tool_name);
            return (
              <li key={`${entry.tool_name}-${entry.timestamp}-${index}`}>
                <Link
                  href={getToolRoute(entry.tool_name)}
                  className="flex items-center gap-3 rounded-xl bg-surface-800/80 px-3 py-2.5 transition-colors hover:bg-surface-700"
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/20 text-secondary">
                    <Icon className="h-4 w-4" />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-sm font-medium text-text-high">
                      {entry.tool_name}
                    </span>
                    <span className="block text-xs text-text-muted">
                      {formatTimestamp(entry.timestamp)}
                    </span>
                  </span>
                  <ExternalLink className="h-3.5 w-3.5 shrink-0 text-text-muted" />
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}

export default UsageHistory;
