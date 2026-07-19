/**
 * Unit tests for dashboard ToolsGrid filtering and ToolCard states.
 */

import "@testing-library/jest-dom";
import { render, screen, fireEvent } from "@testing-library/react";
import { ToolsGrid } from "@/components/features/dashboard";
import type { ToolInfo } from "@/lib/api";

const makeTool = (overrides: Partial<ToolInfo> = {}): ToolInfo => ({
  id: 1,
  name: "Tax Calculator",
  display_name: "Tax Calculator",
  description: "Calculate taxes",
  route: "/tools/tax-calculator",
  is_default: true,
  is_active: true,
  icon: "calculator",
  category: { id: 1, name: "Finance", slug: "finance", color: "text-success", icon: "coins" },
  is_paid: false,
  required_plan: null,
  hasAccess: true,
  ...overrides,
});

const tools: ToolInfo[] = [
  makeTool(),
  makeTool({
    id: 2,
    name: "Character Counter",
    display_name: "Character Counter",
    description: "Count characters",
    category: { id: 2, name: "Writing", slug: "writing", color: "text-info", icon: "pen-line" },
  }),
  makeTool({
    id: 3,
    name: "Premium Analytics",
    display_name: "Premium Analytics",
    description: "Advanced analytics",
    is_paid: true,
    required_plan: { id: 3, name: "Pro", tier_level: 2 },
    hasAccess: false,
  }),
];

const noop = () => {};

describe("ToolsGrid", () => {
  it("renders all tools with no filters", () => {
    render(
      <ToolsGrid
        tools={tools}
        favorites={[]}
        searchQuery=""
        activeCategory="all"
        onToggleFavorite={noop}
      />
    );

    expect(screen.getByText("Tax Calculator")).toBeInTheDocument();
    expect(screen.getByText("Character Counter")).toBeInTheDocument();
    expect(screen.getByText("Premium Analytics")).toBeInTheDocument();
  });

  it("filters by search query", () => {
    render(
      <ToolsGrid
        tools={tools}
        favorites={[]}
        searchQuery="character"
        activeCategory="all"
        onToggleFavorite={noop}
      />
    );

    expect(screen.queryByText("Tax Calculator")).not.toBeInTheDocument();
    expect(screen.getByText("Character Counter")).toBeInTheDocument();
  });

  it("filters by category slug", () => {
    render(
      <ToolsGrid
        tools={tools}
        favorites={[]}
        searchQuery=""
        activeCategory="writing"
        onToggleFavorite={noop}
      />
    );

    expect(screen.queryByText("Tax Calculator")).not.toBeInTheDocument();
    expect(screen.getByText("Character Counter")).toBeInTheDocument();
  });

  it("shows only favorited tools for the favorites filter", () => {
    render(
      <ToolsGrid
        tools={tools}
        favorites={[2]}
        searchQuery=""
        activeCategory="favorites"
        onToggleFavorite={noop}
      />
    );

    expect(screen.queryByText("Tax Calculator")).not.toBeInTheDocument();
    expect(screen.getByText("Character Counter")).toBeInTheDocument();
  });

  it("shows empty state when nothing matches", () => {
    render(
      <ToolsGrid
        tools={tools}
        favorites={[]}
        searchQuery="does-not-exist"
        activeCategory="all"
        onToggleFavorite={noop}
      />
    );

    expect(screen.getByText("No tools match your search.")).toBeInTheDocument();
  });

  it("marks locked paid tools with the required plan", () => {
    render(
      <ToolsGrid
        tools={tools}
        favorites={[]}
        searchQuery=""
        activeCategory="all"
        onToggleFavorite={noop}
      />
    );

    expect(screen.getByText("Requires Pro")).toBeInTheDocument();
  });

  it("invokes onToggleFavorite with the tool id", () => {
    const onToggle = jest.fn();
    render(
      <ToolsGrid
        tools={[makeTool()]}
        favorites={[]}
        searchQuery=""
        activeCategory="all"
        onToggleFavorite={onToggle}
      />
    );

    fireEvent.click(screen.getByLabelText("Add to favorites"));
    expect(onToggle).toHaveBeenCalledWith(1);
  });
});
