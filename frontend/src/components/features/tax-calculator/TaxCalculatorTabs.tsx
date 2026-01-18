"use client";

import { cn } from "@/lib/utils";

export type CalculatorType = "us" | "canada" | "vat";

interface TaxCalculatorTabsProps {
  activeTab: CalculatorType;
  onTabChange: (tab: CalculatorType) => void;
}

const tabs: { id: CalculatorType; label: string; description: string }[] = [
  { id: "us", label: "US Sales Tax", description: "State & local taxes" },
  { id: "canada", label: "Canada GST/PST", description: "Provincial taxes" },
  { id: "vat", label: "VAT", description: "Value Added Tax" },
];

export function TaxCalculatorTabs({ activeTab, onTabChange }: TaxCalculatorTabsProps) {
  return (
    <div className="flex gap-2 rounded-lg bg-surface-800 p-1">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          onClick={() => onTabChange(tab.id)}
          className={cn(
            "flex-1 rounded-md px-4 py-3 text-center transition-all",
            activeTab === tab.id
              ? "bg-primary text-white shadow-lg"
              : "text-text-muted hover:text-text-high hover:bg-surface-700"
          )}
        >
          <div className="font-medium">{tab.label}</div>
          <div className="text-xs opacity-75">{tab.description}</div>
        </button>
      ))}
    </div>
  );
}
