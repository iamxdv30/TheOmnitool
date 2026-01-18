"use client";

import { useState, useMemo } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Button } from "@/components/ui/Button";
import {
  TaxCalculatorTabs,
  ItemList,
  DiscountList,
  TaxSummary,
  ProvinceSelect,
  CANADA_TAX_RATES,
  type CalculatorType,
  type TaxItem,
  type TaxDiscount,
  type TaxSummaryData,
} from "@/components/features/tax-calculator";
import { Calculator, RotateCcw, Truck } from "lucide-react";

interface CalculatorState {
  items: TaxItem[];
  discounts: TaxDiscount[];
  shippingCost: number;
  shippingTaxable: boolean;
  taxRate: number;
  province: string;
  gstRate: number;
  pstRate: number;
  vatRate: number;
}

const initialState: CalculatorState = {
  items: [{ id: crypto.randomUUID(), price: 0 }],
  discounts: [],
  shippingCost: 0,
  shippingTaxable: false,
  taxRate: 0,
  province: "",
  gstRate: 0,
  pstRate: 0,
  vatRate: 20,
};

export default function TaxCalculatorPage() {
  const [activeTab, setActiveTab] = useState<CalculatorType>("us");
  const [state, setState] = useState<CalculatorState>(initialState);

  const updateState = <K extends keyof CalculatorState>(
    key: K,
    value: CalculatorState[K]
  ) => {
    setState((prev) => ({ ...prev, [key]: value }));
  };

  const handleProvinceChange = (province: string, gst: number, pst: number) => {
    setState((prev) => ({
      ...prev,
      province,
      gstRate: gst,
      pstRate: pst,
    }));
  };

  const handleReset = () => {
    setState({
      ...initialState,
      items: [{ id: crypto.randomUUID(), price: 0 }],
    });
  };

  const summary = useMemo((): TaxSummaryData => {
    const itemTotal = state.items.reduce((sum, item) => sum + (item.price || 0), 0);

    let discountTotal = 0;
    for (const discount of state.discounts) {
      if (discount.type === "percentage") {
        discountTotal += itemTotal * (discount.value / 100);
      } else {
        discountTotal += discount.value;
      }
    }
    discountTotal = Math.min(discountTotal, itemTotal);

    const subtotalAfterDiscount = itemTotal - discountTotal;
    const shippingTotal = state.shippingCost || 0;

    let taxBreakdown: { name: string; rate: number; amount: number }[] = [];
    let totalTax = 0;

    const taxableAmount = subtotalAfterDiscount + (state.shippingTaxable ? shippingTotal : 0);

    if (activeTab === "us") {
      if (state.items.some((item) => item.taxRate !== undefined && item.taxRate > 0)) {
        for (const item of state.items) {
          if (item.taxRate && item.price > 0) {
            const itemTax = item.price * (item.taxRate / 100);
            totalTax += itemTax;
          }
        }
        taxBreakdown = [{ name: "Sales Tax", rate: 0, amount: totalTax }];
      } else if (state.taxRate > 0) {
        totalTax = taxableAmount * (state.taxRate / 100);
        taxBreakdown = [{ name: "Sales Tax", rate: state.taxRate, amount: totalTax }];
      }
    } else if (activeTab === "canada") {
      if (state.gstRate > 0) {
        const gstAmount = taxableAmount * (state.gstRate / 100);
        taxBreakdown.push({
          name: state.pstRate > 0 ? "GST" : "HST",
          rate: state.gstRate,
          amount: gstAmount,
        });
        totalTax += gstAmount;
      }
      if (state.pstRate > 0) {
        const pstAmount = taxableAmount * (state.pstRate / 100);
        const pstName = state.province === "QC" ? "QST" : "PST";
        taxBreakdown.push({ name: pstName, rate: state.pstRate, amount: pstAmount });
        totalTax += pstAmount;
      }
    } else if (activeTab === "vat") {
      if (state.vatRate > 0) {
        totalTax = taxableAmount * (state.vatRate / 100);
        taxBreakdown = [{ name: "VAT", rate: state.vatRate, amount: totalTax }];
      }
    }

    const grandTotal = subtotalAfterDiscount + shippingTotal + totalTax;

    return {
      itemTotal,
      discountTotal,
      shippingTotal,
      taxBreakdown,
      totalTax,
      grandTotal,
    };
  }, [state, activeTab]);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-text-high">
            Tax Calculator
          </h1>
          <p className="mt-2 text-text-muted">
            Calculate sales tax, GST/PST, or VAT for your transactions.
          </p>
        </div>
        <Button variant="outline" onClick={handleReset}>
          <RotateCcw className="mr-2 h-4 w-4" />
          Reset
        </Button>
      </div>

      {/* Tax Type Tabs */}
      <TaxCalculatorTabs activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Calculator Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Items */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5 text-primary" />
                Items
              </CardTitle>
              <CardDescription>
                Add items with their prices{activeTab === "us" ? " and optional individual tax rates" : ""}.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ItemList
                items={state.items}
                showItemTaxRate={activeTab === "us"}
                onItemsChange={(items) => updateState("items", items)}
              />
            </CardContent>
          </Card>

          {/* Discounts */}
          <Card>
            <CardHeader>
              <CardTitle>Discounts</CardTitle>
              <CardDescription>
                Add percentage or fixed amount discounts.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DiscountList
                discounts={state.discounts}
                onDiscountsChange={(discounts) => updateState("discounts", discounts)}
              />
            </CardContent>
          </Card>

          {/* Shipping */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Truck className="h-5 w-5 text-primary" />
                Shipping
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <Label htmlFor="shipping">Shipping Cost</Label>
                  <Input
                    id="shipping"
                    type="number"
                    value={state.shippingCost || ""}
                    onChange={(e) =>
                      updateState("shippingCost", parseFloat(e.target.value) || 0)
                    }
                    placeholder="0.00"
                    min={0}
                    step={0.01}
                  />
                </div>
                <div className="flex items-center gap-2 pt-6">
                  <input
                    type="checkbox"
                    id="shippingTaxable"
                    checked={state.shippingTaxable}
                    onChange={(e) => updateState("shippingTaxable", e.target.checked)}
                    className="h-4 w-4 rounded border-surface-700 bg-surface-800 text-primary focus:ring-primary"
                  />
                  <Label htmlFor="shippingTaxable" className="cursor-pointer">
                    Taxable
                  </Label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tax Rate Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Tax Rate</CardTitle>
              <CardDescription>
                {activeTab === "us" && "Enter the sales tax rate or set per-item rates above."}
                {activeTab === "canada" && "Select a province to auto-populate rates."}
                {activeTab === "vat" && "Enter the VAT rate for your region."}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {activeTab === "us" && (
                <div>
                  <Label htmlFor="taxRate">Sales Tax Rate (%)</Label>
                  <Input
                    id="taxRate"
                    type="number"
                    value={state.taxRate || ""}
                    onChange={(e) =>
                      updateState("taxRate", parseFloat(e.target.value) || 0)
                    }
                    placeholder="0.00"
                    min={0}
                    max={100}
                    step={0.01}
                  />
                </div>
              )}

              {activeTab === "canada" && (
                <>
                  <ProvinceSelect
                    value={state.province}
                    onChange={handleProvinceChange}
                  />
                  {state.province && (
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <Label htmlFor="gstRate">
                          {CANADA_TAX_RATES[state.province]?.pst > 0 ? "GST" : "HST"} Rate (%)
                        </Label>
                        <Input
                          id="gstRate"
                          type="number"
                          value={state.gstRate || ""}
                          onChange={(e) =>
                            updateState("gstRate", parseFloat(e.target.value) || 0)
                          }
                          min={0}
                          max={100}
                          step={0.01}
                        />
                      </div>
                      {state.pstRate > 0 && (
                        <div>
                          <Label htmlFor="pstRate">
                            {state.province === "QC" ? "QST" : "PST"} Rate (%)
                          </Label>
                          <Input
                            id="pstRate"
                            type="number"
                            value={state.pstRate || ""}
                            onChange={(e) =>
                              updateState("pstRate", parseFloat(e.target.value) || 0)
                            }
                            min={0}
                            max={100}
                            step={0.01}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}

              {activeTab === "vat" && (
                <div>
                  <Label htmlFor="vatRate">VAT Rate (%)</Label>
                  <Input
                    id="vatRate"
                    type="number"
                    value={state.vatRate || ""}
                    onChange={(e) =>
                      updateState("vatRate", parseFloat(e.target.value) || 0)
                    }
                    placeholder="20.00"
                    min={0}
                    max={100}
                    step={0.01}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Summary Sidebar */}
        <div className="lg:sticky lg:top-8 lg:self-start">
          <TaxSummary data={summary} />
        </div>
      </div>
    </div>
  );
}
