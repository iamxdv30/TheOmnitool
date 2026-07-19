"use client";

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
        "flex shrink-0 items-center gap-1.5 rounded-full border px-5 py-2 text-sm font-medium transition-all duration-200",
        isActive
          ? "border-primary bg-primary text-white shadow-[0_0_15px_rgba(88,129,87,0.4)]"
          : "border-surface-700 bg-transparent text-text-muted hover:border-primary/50 hover:text-text-high"
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
        All Tools
      </Pill>
      <Pill
        isActive={active === "favorites"}
        onClick={() => onChange("favorites")}
      >
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
