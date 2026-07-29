"use client";

import { useState, useCallback } from "react";
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
import { useToolAccess, TOOL_NAMES } from "@/hooks";
import { toolsApi, isSuccess } from "@/lib/api";
import { toast } from "@/store/uiStore";
import { Calculator, RotateCcw, Truck, Loader2 } from "lucide-react";

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

const initialSummary: TaxSummaryData = {
  itemTotal: 0,
  discountTotal: 0,
  shippingTotal: 0,
  taxBreakdown: [],
  totalTax: 0,
  grandTotal: 0,
};

export default function TaxCalculatorPage() {
  // Tool access check
  const { hasAccess, isLoading: isAccessLoading } = useToolAccess(
    TOOL_NAMES.TAX_CALCULATOR
  );

  const [activeTab, setActiveTab] = useState<CalculatorType>("us");
  const [state, setState] = useState<CalculatorState>(initialState);
  const [summary, setSummary] = useState<TaxSummaryData>(initialSummary);
  const [isCalculating, setIsCalculating] = useState(false);

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
    setSummary(initialSummary);
  };

  const calculateTax = useCallback(async () => {
    // Check if there are any items with prices
    const hasItems = state.items.some((item) => item.price > 0);
    if (!hasItems) {
      toast.error("Please add at least one item with a price.");
      return;
    }

    setIsCalculating(true);

    // Build request payload based on calculator type
    const items = state.items
      .filter((item) => item.price > 0)
      .map((item) => ({
        price: item.price,
        tax_rate: activeTab === "us" ? item.taxRate || state.taxRate : undefined,
      }));

    const discounts = state.discounts.map((discount) => ({
      amount: discount.value,
      type: discount.type as "fixed" | "percentage",
    }));

    // Determine tax rates based on calculator type
    let gstRate: number | undefined;
    let pstRate: number | undefined;
    let vatRate: number | undefined;
    let shippingTaxRate: number | undefined;

    if (activeTab === "canada") {
      gstRate = state.gstRate;
      pstRate = state.pstRate;
      shippingTaxRate = state.gstRate + state.pstRate;
    } else if (activeTab === "vat") {
      vatRate = state.vatRate;
    } else {
      // US - use per-item rates or global rate
      shippingTaxRate = state.taxRate;
    }

    const response = await toolsApi.calculateTax({
      calculator_type: activeTab,
      items,
      discounts: discounts.length > 0 ? discounts : undefined,
      shipping_cost: state.shippingCost || undefined,
      shipping_taxable: state.shippingTaxable,
      shipping_tax_rate: state.shippingTaxable ? shippingTaxRate : undefined,
      gst_rate: gstRate,
      pst_rate: pstRate,
      vat_rate: vatRate,
      options: {
        is_sales_before_tax: false,
        discount_is_taxable: true,
      },
    });

    setIsCalculating(false);

    if (isSuccess(response)) {
      const data = response.data;

      // Build tax breakdown for display
      const taxBreakdown: { name: string; rate: number; amount: number }[] = [];

      if (activeTab === "vat") {
        // VAT responses use net/gross/vat_* fields
        const vatAmount = data.vat_amount ?? 0;
        if (vatAmount > 0) {
          taxBreakdown.push({
            name: "VAT",
            rate: data.vat_rate_applied ?? state.vatRate,
            amount: vatAmount,
          });
        }

        setSummary({
          itemTotal: data.item_total,
          discountTotal: data.discount_total,
          shippingTotal: data.shipping_cost,
          taxBreakdown,
          totalTax: vatAmount,
          grandTotal: data.gross_amount ?? 0,
        });
      } else {
        // US / Canada responses use total_tax / total_amount fields.
        // total_tax already includes shipping tax.
        const totalTax = data.total_tax ?? 0;
        const shippingTax = data.shipping_tax ?? 0;
        const itemTax = totalTax - shippingTax;

        if (activeTab === "us") {
          if (itemTax > 0) {
            taxBreakdown.push({
              name: "Sales Tax",
              rate: state.taxRate,
              amount: itemTax,
            });
          }
        } else {
          // Split the combined item tax by the GST/PST rate proportions
          const combinedRate = state.gstRate + state.pstRate;
          if (state.gstRate > 0 && combinedRate > 0) {
            taxBreakdown.push({
              name: state.pstRate > 0 ? "GST" : "HST",
              rate: state.gstRate,
              amount: itemTax * (state.gstRate / combinedRate),
            });
          }
          if (state.pstRate > 0 && combinedRate > 0) {
            taxBreakdown.push({
              name: state.province === "QC" ? "QST" : "PST",
              rate: state.pstRate,
              amount: itemTax * (state.pstRate / combinedRate),
            });
          }
        }

        if (shippingTax > 0) {
          taxBreakdown.push({
            name: "Shipping Tax",
            rate: activeTab === "us" ? state.taxRate : state.gstRate + state.pstRate,
            amount: shippingTax,
          });
        }

        setSummary({
          itemTotal: data.item_total,
          discountTotal: data.discount_total,
          shippingTotal: data.shipping_cost,
          taxBreakdown,
          totalTax,
          grandTotal: data.total_amount ?? 0,
        });
      }

      toast.success("Calculation complete!");
    } else {
      toast.error(response.message || "Failed to calculate tax.");
    }
  }, [state, activeTab]);

  // Show loading while checking access
  if (isAccessLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Access denied will redirect, but just in case
  if (!hasAccess) {
    return null;
  }

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
                Add items with their prices
                {activeTab === "us" ? " and optional individual tax rates" : ""}.
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
                {activeTab === "us" &&
                  "Enter the sales tax rate or set per-item rates above."}
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
                          {CANADA_TAX_RATES[state.province]?.pst > 0 ? "GST" : "HST"}{" "}
                          Rate (%)
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

          {/* Calculate Button */}
          <Button
            onClick={calculateTax}
            disabled={isCalculating}
            className="w-full"
            size="lg"
          >
            {isCalculating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Calculating...
              </>
            ) : (
              <>
                <Calculator className="mr-2 h-4 w-4" />
                Calculate Tax
              </>
            )}
          </Button>
        </div>

        {/* Summary Sidebar */}
        <div className="lg:sticky lg:top-8 lg:self-start">
          <TaxSummary data={summary} />
        </div>
      </div>
    </div>
  );
}
