"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ArrowRight, Loader2, Pin } from "lucide-react";
import { toolsApi, isSuccess, type ToolInfo } from "@/lib/api";
import { toast } from "@/store/uiStore";
import { useAuth } from "@/hooks";
import { Button, Card, CardContent } from "@/components/ui";
import {
  ToolCard,
  UsageHistory,
  UpgradeBanner,
} from "@/components/features/dashboard";
import type { UsageHistoryEntry } from "@/types";

export default function DashboardPage() {
  const { user } = useAuth();
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [favorites, setFavorites] = useState<number[]>([]);
  const [history, setHistory] = useState<UsageHistoryEntry[]>([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setIsLoading(true);
      setIsHistoryLoading(true);

      const [toolsRes, favoritesRes, historyRes] = await Promise.all([
        toolsApi.listTools(),
        toolsApi.getFavorites(),
        toolsApi.getUsageHistory(8),
      ]);

      if (cancelled) return;

      if (isSuccess(toolsRes)) setTools(toolsRes.data.tools);
      if (isSuccess(favoritesRes)) setFavorites(favoritesRes.data.favorites);
      if (isSuccess(historyRes)) {
        setHistory(historyRes.data.history);
        setHistoryTotal(historyRes.data.total);
      }

      setIsLoading(false);
      setIsHistoryLoading(false);
    }

    loadDashboard();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleToggleFavorite = useCallback(
    async (toolId: number) => {
      const isFavorite = favorites.includes(toolId);

      setFavorites((previous) =>
        isFavorite
          ? previous.filter((id) => id !== toolId)
          : [...previous, toolId]
      );

      const response = isFavorite
        ? await toolsApi.removeFavorite(toolId)
        : await toolsApi.addFavorite(toolId);

      if (response.status === "error") {
        setFavorites((previous) =>
          isFavorite
            ? [...previous, toolId]
            : previous.filter((id) => id !== toolId)
        );
        toast.error(response.message || "Could not update favorites.");
      }
    },
    [favorites]
  );

  const pinnedTools = useMemo(
    () => tools.filter((tool) => favorites.includes(tool.id)),
    [favorites, tools]
  );
  const displayName = user?.fname || user?.username || "there";

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-5 border-b border-surface-700 pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.1em] text-primary">
            Your workspace
          </p>
          <h1 className="mt-2 font-display text-3xl font-bold text-text-high sm:text-4xl">
            Welcome back, {displayName}
          </h1>
          <p className="mt-2 text-base text-text-muted">
            Continue where you left off or find a utility for your next task.
          </p>
        </div>
        <Link href="/tools">
          <Button variant="outline">
            Browse all tools
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Button>
        </Link>
      </header>

      <UpgradeBanner tools={tools} />

      <div className="grid gap-8 xl:grid-cols-[minmax(0,1.5fr)_minmax(20rem,0.85fr)]">
        <section aria-labelledby="pinned-tools-heading">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 text-primary">
                <Pin className="h-4 w-4" aria-hidden="true" />
                <p className="text-xs font-semibold uppercase tracking-[0.1em]">
                  Quick access
                </p>
              </div>
              <h2
                id="pinned-tools-heading"
                className="mt-2 font-display text-2xl font-bold text-text-high"
              >
                Pinned tools
              </h2>
            </div>
            <span className="font-mono text-sm text-text-muted">
              {pinnedTools.length} pinned
            </span>
          </div>

          {isLoading ? (
            <div className="flex min-h-52 items-center justify-center">
              <Loader2 className="h-7 w-7 animate-spin text-primary" />
            </div>
          ) : pinnedTools.length > 0 ? (
            <div className="grid gap-4 sm:grid-cols-2">
              {pinnedTools.slice(0, 4).map((tool) => (
                <ToolCard
                  key={tool.id}
                  tool={tool}
                  isFavorite
                  onToggleFavorite={handleToggleFavorite}
                />
              ))}
            </div>
          ) : (
            <Card variant="glass" padding="lg" className="rounded-2xl">
              <CardContent className="flex flex-col items-start gap-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/15 text-secondary">
                  <Pin className="h-5 w-5" aria-hidden="true" />
                </div>
                <div>
                  <h3 className="font-display text-lg font-bold text-text-high">
                    Pin your most-used tools
                  </h3>
                  <p className="mt-1 text-sm leading-relaxed text-text-muted">
                    Save tools from the library to keep your regular work close at hand.
                  </p>
                </div>
                <Link href="/tools">
                  <Button variant="outline" size="sm">
                    Explore tools
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </section>

        <section aria-labelledby="recent-activity-heading">
          <h2 id="recent-activity-heading" className="sr-only">
            Recent activity
          </h2>
          <UsageHistory
            history={history}
            totalCount={historyTotal}
            isLoading={isHistoryLoading}
          />
        </section>
      </div>
    </div>
  );
}
