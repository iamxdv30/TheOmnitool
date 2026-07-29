"use client";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Plus, Trash2 } from "lucide-react";

export interface TaxItem {
  id: string;
  price: number;
  taxRate?: number;
}

interface ItemListProps {
  items: TaxItem[];
  showItemTaxRate?: boolean;
  onItemsChange: (items: TaxItem[]) => void;
}

export function ItemList({ items, showItemTaxRate = false, onItemsChange }: ItemListProps) {
  const addItem = () => {
    const newItem: TaxItem = {
      id: crypto.randomUUID(),
      price: 0,
      taxRate: showItemTaxRate ? 0 : undefined,
    };
    onItemsChange([...items, newItem]);
  };

  const removeItem = (id: string) => {
    if (items.length > 1) {
      onItemsChange(items.filter((item) => item.id !== id));
    }
  };

  const updateItem = (id: string, field: keyof TaxItem, value: number) => {
    onItemsChange(
      items.map((item) =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label>Items</Label>
        <Button type="button" variant="ghost" size="sm" onClick={addItem}>
          <Plus className="mr-1 h-4 w-4" />
          Add Item
        </Button>
      </div>

      <div className="space-y-2">
        {items.map((item, index) => (
          <div key={item.id} className="flex items-center gap-2">
            <div className="flex-1">
              <Input
                type="number"
                placeholder={`Item ${index + 1} price`}
                value={item.price || ""}
                onChange={(e) =>
                  updateItem(item.id, "price", parseFloat(e.target.value) || 0)
                }
                min={0}
                step={0.01}
              />
            </div>
            {showItemTaxRate && (
              <div className="w-24">
                <Input
                  type="number"
                  placeholder="Tax %"
                  value={item.taxRate || ""}
                  onChange={(e) =>
                    updateItem(item.id, "taxRate", parseFloat(e.target.value) || 0)
                  }
                  min={0}
                  max={100}
                  step={0.01}
                />
              </div>
            )}
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => removeItem(item.id)}
              disabled={items.length === 1}
              className="text-danger hover:text-danger hover:bg-danger/10"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
