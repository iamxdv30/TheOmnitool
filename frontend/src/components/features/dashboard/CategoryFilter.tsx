"use client";

import { Heart, LayoutGrid } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Category } from "@/types";

export type CategoryFilterValue = "all" | "favorites" | string;

export interface CategoryFilterProps {
  categories: Category[];
  active: CategoryFilterValue;
  onChange: (value: CategoryFilterValue) => void;
  className?: string;
}

function Pill({
  isActive,
  onClick,
  children,
}: {
  isActive: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={isActive}
      className={cn(
        "flex shrink-0 items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-all duration-200",
        isActive
          ? "border-primary bg-primary/15 text-primary"
          : "border-surface-700 bg-surface-800 text-text-muted hover:border-primary/50 hover:text-text-high"
      )}
    >
      {children}
    </button>
  );
}

/**
 * Filter pills: All Tools, Favorites, then one pill per active category.
 */
export function CategoryFilter({
  categories,
  active,
  onChange,
  className,
}: CategoryFilterProps) {
  return (
    <div
      role="group"
      aria-label="Filter tools by category"
      className={cn("flex flex-wrap items-center gap-2", className)}
    >
      <Pill isActive={active === "all"} onClick={() => onChange("all")}>
        <LayoutGrid className="h-3.5 w-3.5" />
        All Tools
      </Pill>
      <Pill
        isActive={active === "favorites"}
        onClick={() => onChange("favorites")}
      >
        <Heart className="h-3.5 w-3.5" />
        Favorites
      </Pill>
      {categories.map((category) => (
        <Pill
          key={category.id}
          isActive={active === category.slug}
          onClick={() => onChange(category.slug)}
        >
          {category.name}
        </Pill>
      ))}
    </div>
  );
}

export default CategoryFilter;
