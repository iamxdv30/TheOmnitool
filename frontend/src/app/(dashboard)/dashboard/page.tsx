"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/hooks";
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
import { Loader2 } from "lucide-react";
import type { Category, UsageHistoryEntry } from "@/types";

export default function DashboardPage() {
  const { user } = useAuth();

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
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-display text-3xl font-bold text-text-high">
          Tools Discovery
        </h1>
        <p className="mt-2 text-text-muted">
          Welcome back, {user?.username || "User"}. Find, favorite, and launch
          your tools.
        </p>
      </div>

      <UpgradeBanner tools={tools} />

      {/* Search + filters */}
      <div className="space-y-4">
        <SearchInput onSearch={setSearchQuery} placeholder="Search tools..." />
        <CategoryFilter
          categories={categories}
          active={activeCategory}
          onChange={setActiveCategory}
        />
      </div>

      {/* Tools grid */}
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

      {/* Usage & history */}
      <UsageHistory
        history={history}
        totalCount={historyTotal}
        isLoading={isHistoryLoading}
      />
    </div>
  );
}
