"use client";

import type { ReactNode } from "react";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-surface-900">
      <main>{children}</main>
    </div>
  );
}
