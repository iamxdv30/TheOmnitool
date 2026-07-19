"use client";

import { createElement } from "react";
import Link from "next/link";
import { ArrowRight, Heart, Lock } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge } from "@/components/ui";
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
      className={cn(
        "relative h-full transition-all",
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

      <CardHeader>
        <div
          className={cn(
            "mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-surface-700",
            tool.category?.color || "text-primary"
          )}
        >
          {createElement(getToolIcon(tool.icon, tool.name), {
            className: "h-5 w-5",
          })}
        </div>
        <CardTitle className="pr-8 text-lg">{tool.display_name}</CardTitle>
        <CardDescription className="line-clamp-2">
          {tool.description}
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="flex items-center justify-between gap-2">
          {locked ? (
            <span className="flex items-center text-sm text-warning">
              <Lock className="mr-1 h-4 w-4" />
              {tool.is_paid && tool.required_plan?.name
                ? `Requires ${tool.required_plan.name}`
                : "No access"}
            </span>
          ) : (
            <span className="flex items-center text-sm text-primary">
              Launch
              <ArrowRight className="ml-1 h-4 w-4" />
            </span>
          )}
          {tool.category?.name && (
            <Badge
              variant="outline"
              className={cn("shrink-0", tool.category.color || "text-text-muted")}
            >
              {tool.category.name}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );

  if (locked) {
    return <div aria-disabled="true">{cardBody}</div>;
  }

  return <Link href={route}>{cardBody}</Link>;
}

export default ToolCard;
