"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui";
import { Receipt } from "lucide-react";

export interface TaxBreakdown {
  name: string;
  rate: number;
  amount: number;
}

export interface TaxSummaryData {
  itemTotal: number;
  discountTotal: number;
  shippingTotal: number;
  taxBreakdown: TaxBreakdown[];
  totalTax: number;
  grandTotal: number;
}

interface TaxSummaryProps {
  data: TaxSummaryData;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

export function TaxSummary({ data }: TaxSummaryProps) {
  return (
    <Card variant="glass">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Receipt className="h-5 w-5 text-primary" />
          Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <SummaryRow label="Subtotal" value={formatCurrency(data.itemTotal)} />
        
        {data.discountTotal > 0 && (
          <SummaryRow
            label="Discounts"
            value={`-${formatCurrency(data.discountTotal)}`}
            className="text-success"
          />
        )}
        
        {data.shippingTotal > 0 && (
          <SummaryRow label="Shipping" value={formatCurrency(data.shippingTotal)} />
        )}

        <div className="border-t border-surface-700 pt-3">
          {data.taxBreakdown.map((tax, index) => (
            <SummaryRow
              key={index}
              label={`${tax.name} (${tax.rate}%)`}
              value={formatCurrency(tax.amount)}
              className="text-text-muted"
            />
          ))}
          <SummaryRow
            label="Total Tax"
            value={formatCurrency(data.totalTax)}
            className="font-medium"
          />
        </div>

        <div className="border-t border-surface-700 pt-3">
          <SummaryRow
            label="Grand Total"
            value={formatCurrency(data.grandTotal)}
            className="text-lg font-bold text-primary"
          />
        </div>
      </CardContent>
    </Card>
  );
}

interface SummaryRowProps {
  label: string;
  value: string;
  className?: string;
}

function SummaryRow({ label, value, className = "" }: SummaryRowProps) {
  return (
    <div className={`flex items-center justify-between ${className}`}>
      <span className="text-text-muted">{label}</span>
      <span className="text-text-high">{value}</span>
    </div>
  );
}
