"use client";

import type { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Sidebar } from "@/components/layout";
import { useAuth } from "@/hooks";
import { Loader2 } from "lucide-react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-surface-900">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const isAdmin = user?.role === "admin" || user?.role === "superadmin";

  return (
    <div className="min-h-screen bg-surface-900">
      <Sidebar isAdmin={isAdmin} />
      <main className="min-h-screen p-4 pt-20 md:ml-64 md:p-8 md:pt-8">{children}</main>
    </div>
  );
}
