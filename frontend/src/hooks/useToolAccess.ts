"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { toast } from "@/store/uiStore";

interface UseToolAccessOptions {
  redirectTo?: string;
  showToast?: boolean;
}

interface UseToolAccessReturn {
  hasAccess: boolean;
  isLoading: boolean;
  isAdmin: boolean;
}

/**
 * Hook to check if the current user has access to a specific tool.
 *
 * Admins and superadmins have access to all tools.
 * Regular users need the tool in their permissions array.
 *
 * @param toolName - The name of the tool to check access for
 * @param options - Configuration options
 * @returns Object with hasAccess, isLoading, and isAdmin flags
 *
 * @example
 * ```tsx
 * function TaxCalculatorPage() {
 *   const { hasAccess, isLoading } = useToolAccess("Tax Calculator");
 *
 *   if (isLoading) return <Loading />;
 *   if (!hasAccess) return null; // Will redirect automatically
 *
 *   return <TaxCalculatorContent />;
 * }
 * ```
 */
export function useToolAccess(
  toolName: string,
  options: UseToolAccessOptions = {}
): UseToolAccessReturn {
  const { redirectTo = "/dashboard", showToast = true } = options;
  const router = useRouter();

  const user = useAuthStore((state) => state.user);
  const permissions = useAuthStore((state) => state.permissions);
  const isInitialized = useAuthStore((state) => state.isInitialized);
  const isAuthLoading = useAuthStore((state) => state.isLoading);

  // Check if user is admin/superadmin
  const isAdmin = user?.role === "admin" || user?.role === "superadmin";

  // Admins have access to all tools
  const hasAccess = isAdmin || permissions.includes(toolName);

  // Loading until auth state is initialized (derived — no extra state needed)
  const isLoading = !isInitialized || isAuthLoading;

  useEffect(() => {
    // Wait until auth is initialized
    if (!isInitialized || isAuthLoading) {
      return;
    }

    // If user doesn't have access, redirect
    if (!hasAccess) {
      if (showToast) {
        toast.error(`You don't have access to ${toolName}.`);
      }
      router.push(redirectTo);
    }
  }, [isInitialized, isAuthLoading, hasAccess, toolName, redirectTo, showToast, router]);

  return {
    hasAccess,
    isLoading,
    isAdmin,
  };
}

/**
 * Tool name constants for type safety
 */
export const TOOL_NAMES = {
  TAX_CALCULATOR: "Tax Calculator",
  UNIFIED_TAX_CALCULATOR: "Unified Tax Calculator",
  CANADA_TAX_CALCULATOR: "Canada Tax Calculator",
  CHARACTER_COUNTER: "Character Counter",
  EMAIL_TEMPLATES: "Email Templates",
  UNIX_TIMESTAMP_CONVERTER: "Unix Timestamp Converter",
} as const;

export type ToolName = (typeof TOOL_NAMES)[keyof typeof TOOL_NAMES];
