"use client";

import type { ReactNode } from "react";
import { Header } from "@/components/layout";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-surface-900">
      <Header />
      <main className="pt-16">{children}</main>
    </div>
  );
}
