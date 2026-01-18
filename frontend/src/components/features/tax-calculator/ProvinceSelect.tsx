"use client";

import { Label } from "@/components/ui/Label";

export const CANADA_TAX_RATES: Record<string, { gst: number; pst: number; name: string }> = {
  AB: { gst: 5, pst: 0, name: "Alberta" },
  BC: { gst: 5, pst: 7, name: "British Columbia" },
  MB: { gst: 5, pst: 7, name: "Manitoba" },
  NB: { gst: 15, pst: 0, name: "New Brunswick (HST)" },
  NL: { gst: 15, pst: 0, name: "Newfoundland and Labrador (HST)" },
  NT: { gst: 5, pst: 0, name: "Northwest Territories" },
  NS: { gst: 15, pst: 0, name: "Nova Scotia (HST)" },
  NU: { gst: 5, pst: 0, name: "Nunavut" },
  ON: { gst: 13, pst: 0, name: "Ontario (HST)" },
  PE: { gst: 15, pst: 0, name: "Prince Edward Island (HST)" },
  QC: { gst: 5, pst: 9.975, name: "Quebec (GST + QST)" },
  SK: { gst: 5, pst: 6, name: "Saskatchewan" },
  YT: { gst: 5, pst: 0, name: "Yukon" },
};

interface ProvinceSelectProps {
  value: string;
  onChange: (province: string, gst: number, pst: number) => void;
}

export function ProvinceSelect({ value, onChange }: ProvinceSelectProps) {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const provinceCode = e.target.value;
    if (provinceCode && CANADA_TAX_RATES[provinceCode]) {
      const rates = CANADA_TAX_RATES[provinceCode];
      onChange(provinceCode, rates.gst, rates.pst);
    } else {
      onChange("", 0, 0);
    }
  };

  return (
    <div className="space-y-2">
      <Label htmlFor="province">Province/Territory</Label>
      <select
        id="province"
        value={value}
        onChange={handleChange}
        className="w-full rounded-lg border border-surface-700 bg-surface-800 px-3 py-2 text-text-high transition-colors hover:border-primary/50 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary-glow focus:ring-offset-2 focus:ring-offset-surface-900"
      >
        <option value="">Select a province...</option>
        {Object.entries(CANADA_TAX_RATES).map(([code, { name }]) => (
          <option key={code} value={code}>
            {name}
          </option>
        ))}
      </select>
    </div>
  );
}
