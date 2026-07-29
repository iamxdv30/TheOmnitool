"use client";

import { useMemo } from "react";
import { SearchX } from "lucide-react";
import { Card, CardContent } from "@/components/ui";
import type { ToolInfo } from "@/lib/api";
import { ToolCard } from "./ToolCard";
import type { CategoryFilterValue } from "./CategoryFilter";

export interface ToolsGridProps {
  tools: ToolInfo[];
  favorites: number[];
  searchQuery: string;
  activeCategory: CategoryFilterValue;
  onToggleFavorite: (toolId: number) => void;
}

/**
 * Responsive tool grid (1 col mobile / 2 tablet / 3 desktop) with
 * search + category/favorites filtering.
 */
export function ToolsGrid({
  tools,
  favorites,
  searchQuery,
  activeCategory,
  onToggleFavorite,
}: ToolsGridProps) {
  const filtered = useMemo(() => {
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
    });
  }, [tools, favorites, searchQuery, activeCategory]);

  if (filtered.length === 0) {
    return (
      <Card variant="glass">
        <CardContent className="flex flex-col items-center justify-center py-12">
          <SearchX className="mb-4 h-12 w-12 text-text-muted" />
          <p className="text-center text-text-muted">
            {activeCategory === "favorites" && !searchQuery
              ? "No favorites yet. Tap the heart on a tool to pin it here."
              : "No tools match your search."}
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {filtered.map((tool) => (
        <ToolCard
          key={tool.id}
          tool={tool}
          isFavorite={favorites.includes(tool.id)}
          onToggleFavorite={onToggleFavorite}
        />
      ))}
    </div>
  );
}

export default ToolsGrid;
