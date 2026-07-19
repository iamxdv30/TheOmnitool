"use client";

import { useCallback, useEffect, useState } from "react";
import { toolsApi, isSuccess, type ToolInfo } from "@/lib/api";
import { toast } from "@/store/uiStore";
import { SearchInput } from "@/components/ui";
import {
  CategoryFilter,
  ToolsGrid,
  UsageHistory,
  UpgradeBanner,
  type CategoryFilterValue,
} from "@/components/features/dashboard";
import { LayoutGrid, Loader2 } from "lucide-react";
import type { Category, UsageHistoryEntry } from "@/types";

export default function DashboardPage() {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [favorites, setFavorites] = useState<number[]>([]);
  const [history, setHistory] = useState<UsageHistoryEntry[]>([]);
  const [historyTotal, setHistoryTotal] = useState(0);

  const [searchQuery, setSearchQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<CategoryFilterValue>("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isHistoryLoading, setIsHistoryLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setIsLoading(true);
      setIsHistoryLoading(true);

      const [toolsRes, categoriesRes, favoritesRes, historyRes] =
        await Promise.all([
          toolsApi.listTools(),
          toolsApi.getCategories(),
          toolsApi.getFavorites(),
          toolsApi.getUsageHistory(8),
        ]);

      if (cancelled) return;

      if (isSuccess(toolsRes)) setTools(toolsRes.data.tools);
      if (isSuccess(categoriesRes)) setCategories(categoriesRes.data.categories);
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

      // Optimistic update, rolled back on failure
      setFavorites((prev) =>
        isFavorite ? prev.filter((id) => id !== toolId) : [...prev, toolId]
      );

      const response = isFavorite
        ? await toolsApi.removeFavorite(toolId)
        : await toolsApi.addFavorite(toolId);

      if (response.status === "error") {
        setFavorites((prev) =>
          isFavorite ? [...prev, toolId] : prev.filter((id) => id !== toolId)
        );
        toast.error(response.message || "Could not update favorites.");
      }
    },
    [favorites]
  );

  return (
    <div className="space-y-10">
      {/* Centered hero */}
      <div className="pt-6 text-center">
        <h1 className="font-display text-4xl font-bold text-text-high sm:text-5xl">
          Tools Discovery
        </h1>
        <p className="mt-3 text-lg text-text-muted">
          Find the perfect utility for your next task.
        </p>
      </div>

      <UpgradeBanner tools={tools} />

      {/* Search + filters */}
      <div className="space-y-6">
        <SearchInput
          variant="hero"
          onSearch={setSearchQuery}
          placeholder="Search tools..."
          className="mx-auto max-w-2xl"
        />
        <CategoryFilter
          categories={categories}
          active={activeCategory}
          onChange={setActiveCategory}
          className="justify-center"
        />
      </div>

      {/* Available tools */}
      <section>
        <div className="mb-6 flex items-center justify-between border-b border-surface-700 pb-3">
          <h2 className="flex items-center gap-2.5 font-display text-xl font-bold text-text-high">
            <LayoutGrid className="h-5 w-5 text-primary" />
            Available Tools
          </h2>
          <span className="font-mono text-sm text-primary">
            Total: {tools.length}
          </span>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          <ToolsGrid
            tools={tools}
            favorites={favorites}
            searchQuery={searchQuery}
            activeCategory={activeCategory}
            onToggleFavorite={handleToggleFavorite}
          />
        )}
      </section>

      {/* Usage & history */}
      <UsageHistory
        history={history}
        totalCount={historyTotal}
        isLoading={isHistoryLoading}
      />
    </div>
  );
}
