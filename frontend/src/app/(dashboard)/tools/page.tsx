"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { LayoutGrid, Loader2 } from "lucide-react";
import { toolsApi, isSuccess, type ToolInfo } from "@/lib/api";
import { toast } from "@/store/uiStore";
import { SearchInput } from "@/components/ui";
import {
  CategoryFilter,
  ToolsGrid,
  UpgradeBanner,
  type CategoryFilterValue,
} from "@/components/features/dashboard";
import type { Category } from "@/types";

export default function ToolsPage() {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [favorites, setFavorites] = useState<number[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeCategory, setActiveCategory] =
    useState<CategoryFilterValue>("all");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadTools() {
      setIsLoading(true);

      const [toolsRes, categoriesRes, favoritesRes] = await Promise.all([
        toolsApi.listTools(),
        toolsApi.getCategories(),
        toolsApi.getFavorites(),
      ]);

      if (cancelled) return;

      if (isSuccess(toolsRes)) setTools(toolsRes.data.tools);
      if (isSuccess(categoriesRes)) setCategories(categoriesRes.data.categories);
      if (isSuccess(favoritesRes)) setFavorites(favoritesRes.data.favorites);

      setIsLoading(false);
    }

    loadTools();
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

  const filteredToolCount = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    return tools.filter((tool) => {
      if (activeCategory === "favorites" && !favorites.includes(tool.id)) {
        return false;
      }
      if (
        activeCategory !== "all" &&
        activeCategory !== "favorites" &&
        tool.category?.slug !== activeCategory
      ) {
        return false;
      }
      if (!query) return true;
      return (
        tool.display_name.toLowerCase().includes(query) ||
        tool.name.toLowerCase().includes(query) ||
        (tool.description || "").toLowerCase().includes(query)
      );
    }).length;
  }, [activeCategory, favorites, searchQuery, tools]);

  return (
    <div className="space-y-8">
      <header className="border-b border-surface-700 pb-6">
        <p className="text-xs font-semibold uppercase tracking-[0.1em] text-primary">
          Tool library
        </p>
        <div className="mt-2 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="font-display text-3xl font-bold text-text-high sm:text-4xl">
              All tools
            </h1>
            <p className="mt-2 text-base text-text-muted">
              Search, filter, and launch the utilities available to you.
            </p>
          </div>
          <span className="font-mono text-sm text-text-muted" aria-live="polite">
            {filteredToolCount} {filteredToolCount === 1 ? "tool" : "tools"} available
          </span>
        </div>
      </header>

      <UpgradeBanner tools={tools} />

      <section aria-labelledby="tool-search-heading" className="space-y-4">
        <h2 id="tool-search-heading" className="sr-only">
          Search and filter tools
        </h2>
        <SearchInput
          onSearch={setSearchQuery}
          placeholder="Search tools..."
          className="max-w-2xl"
        />
        <CategoryFilter
          categories={categories}
          active={activeCategory}
          onChange={setActiveCategory}
        />
      </section>

      <section aria-labelledby="tool-results-heading">
        <div className="mb-5 flex items-center gap-2 border-b border-surface-700 pb-3">
          <LayoutGrid className="h-5 w-5 text-primary" aria-hidden="true" />
          <h2 id="tool-results-heading" className="font-display text-xl font-bold text-text-high">
            Results
          </h2>
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
    </div>
  );
}
