"use client";

import { History, Activity } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui";
import type { UsageHistoryEntry } from "@/types";
import { getToolIcon } from "./toolMaps";

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
    <Card variant="glass">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <History className="h-5 w-5 text-secondary" />
            Usage &amp; History
          </CardTitle>
          <span className="flex items-center gap-1.5 text-sm text-text-muted">
            <Activity className="h-4 w-4" />
            {totalCount} total
          </span>
        </div>
        <CardDescription>Your recent tool activity</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="py-4 text-center text-sm text-text-muted">Loading…</p>
        ) : history.length === 0 ? (
          <p className="py-4 text-center text-sm text-text-muted">
            No activity yet — launch a tool to get started.
          </p>
        ) : (
          <ul className="divide-y divide-surface-700">
            {history.map((entry, index) => {
              const Icon = getToolIcon(null, entry.tool_name);
              return (
                <li
                  key={`${entry.tool_name}-${entry.timestamp}-${index}`}
                  className="flex items-center gap-3 py-2.5"
                >
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-surface-700 text-secondary">
                    <Icon className="h-4 w-4" />
                  </span>
                  <span className="min-w-0 flex-1 truncate text-sm text-text-high">
                    {entry.tool_name}
                  </span>
                  <span className="shrink-0 text-xs text-text-muted">
                    {formatTimestamp(entry.timestamp)}
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

export default UsageHistory;
