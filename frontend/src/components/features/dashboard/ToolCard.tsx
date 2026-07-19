"use client";

import { createElement } from "react";
import Link from "next/link";
import { ArrowRight, Heart, Lock } from "lucide-react";
import { Card } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { ToolInfo } from "@/lib/api";
import { getToolIcon, getToolRoute } from "./toolMaps";

export interface ToolCardProps {
  tool: ToolInfo;
  isFavorite: boolean;
  onToggleFavorite: (toolId: number) => void;
}

/**
 * Tool card with favorite toggle, category badge, and paid/locked indicator.
 */
export function ToolCard({ tool, isFavorite, onToggleFavorite }: ToolCardProps) {
  const locked = !tool.hasAccess;
  const route = getToolRoute(tool.name);

  const cardBody = (
    <Card
      variant="interactive"
      padding="lg"
      className={cn(
        "relative flex h-full flex-col rounded-2xl transition-all",
        locked ? "opacity-70 hover:border-surface-700" : "hover:border-primary/50"
      )}
    >
      <button
        type="button"
        aria-label={isFavorite ? "Remove from favorites" : "Add to favorites"}
        aria-pressed={isFavorite}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          onToggleFavorite(tool.id);
        }}
        className="absolute right-3 top-3 z-10 rounded-full p-1.5 text-text-muted transition-colors hover:bg-surface-700 hover:text-danger"
      >
        <Heart
          className={cn("h-4 w-4", isFavorite && "fill-danger text-danger")}
        />
      </button>

      <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/20 text-secondary">
        {createElement(getToolIcon(tool.icon, tool.name), {
          className: "h-6 w-6",
        })}
      </div>

      <h3 className="font-display text-xl font-bold text-text-high">
        {tool.display_name}
      </h3>
      <p className="mt-2 line-clamp-2 flex-1 text-sm leading-relaxed text-text-muted">
        {tool.description}
      </p>

      <div className="mt-6 flex items-center justify-between gap-2">
        {tool.category?.name ? (
          <span className="shrink-0 rounded bg-surface-700/70 px-2.5 py-1 font-mono text-xs text-text-muted">
            {tool.category.name}
          </span>
        ) : (
          <span />
        )}
        {locked ? (
          <span className="flex items-center text-sm text-warning">
            <Lock className="mr-1 h-4 w-4" />
            {tool.is_paid && tool.required_plan?.name
              ? `Requires ${tool.required_plan.name}`
              : "No access"}
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-sm font-medium text-text-high transition-colors group-hover:text-primary">
            Launch
            <ArrowRight className="h-4 w-4" />
          </span>
        )}
      </div>
    </Card>
  );

  if (locked) {
    return <div aria-disabled="true">{cardBody}</div>;
  }

  return (
    <Link href={route} className="group">
      {cardBody}
    </Link>
  );
}

export default ToolCard;
