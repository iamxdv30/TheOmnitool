"use client";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Plus, Trash2, Percent, DollarSign } from "lucide-react";

export interface TaxDiscount {
  id: string;
  type: "percentage" | "fixed";
  value: number;
}

interface DiscountListProps {
  discounts: TaxDiscount[];
  onDiscountsChange: (discounts: TaxDiscount[]) => void;
}

export function DiscountList({ discounts, onDiscountsChange }: DiscountListProps) {
  const addDiscount = () => {
    const newDiscount: TaxDiscount = {
      id: crypto.randomUUID(),
      type: "percentage",
      value: 0,
    };
    onDiscountsChange([...discounts, newDiscount]);
  };

  const removeDiscount = (id: string) => {
    onDiscountsChange(discounts.filter((d) => d.id !== id));
  };

  const updateDiscount = (id: string, field: keyof TaxDiscount, value: string | number) => {
    onDiscountsChange(
      discounts.map((d) =>
        d.id === id ? { ...d, [field]: value } : d
      )
    );
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label>Discounts (optional)</Label>
        <Button type="button" variant="ghost" size="sm" onClick={addDiscount}>
          <Plus className="mr-1 h-4 w-4" />
          Add Discount
        </Button>
      </div>

      {discounts.length === 0 ? (
        <p className="text-sm text-text-muted">No discounts added</p>
      ) : (
        <div className="space-y-2">
          {discounts.map((discount) => (
            <div key={discount.id} className="flex items-center gap-2">
              <div className="flex rounded-lg border border-surface-700 overflow-hidden">
                <button
                  type="button"
                  onClick={() => updateDiscount(discount.id, "type", "percentage")}
                  className={`px-3 py-2 transition-colors ${
                    discount.type === "percentage"
                      ? "bg-primary text-white"
                      : "bg-surface-800 text-text-muted hover:text-text-high"
                  }`}
                >
                  <Percent className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={() => updateDiscount(discount.id, "type", "fixed")}
                  className={`px-3 py-2 transition-colors ${
                    discount.type === "fixed"
                      ? "bg-primary text-white"
                      : "bg-surface-800 text-text-muted hover:text-text-high"
                  }`}
                >
                  <DollarSign className="h-4 w-4" />
                </button>
              </div>
              <div className="flex-1">
                <Input
                  type="number"
                  placeholder={discount.type === "percentage" ? "Discount %" : "Amount"}
                  value={discount.value || ""}
                  onChange={(e) =>
                    updateDiscount(discount.id, "value", parseFloat(e.target.value) || 0)
                  }
                  min={0}
                  max={discount.type === "percentage" ? 100 : undefined}
                  step={0.01}
                />
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeDiscount(discount.id)}
                className="text-danger hover:text-danger hover:bg-danger/10"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
