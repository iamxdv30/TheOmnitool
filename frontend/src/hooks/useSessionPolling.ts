"use client";

import { useEffect, useRef, useCallback } from "react";
import { useAuthStore } from "@/store/authStore";
import authApi from "@/lib/api/auth";

/**
 * Session Polling Hook
 * Based on Phase 3 spec (Section 4.6)
 * 
 * - Polls /auth/status every 5 minutes to detect session expiration
 * - Only polls when user is authenticated
 * - Pauses polling when tab is not visible
 * - Clears state and redirects on session expiration
 */

const POLLING_INTERVAL = 5 * 60 * 1000; // 5 minutes in milliseconds

interface UseSessionPollingOptions {
  enabled?: boolean;
  interval?: number;
}

export function useSessionPolling(options: UseSessionPollingOptions = {}) {
  const { enabled = true, interval = POLLING_INTERVAL } = options;

  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isInitialized = useAuthStore((state) => state.isInitialized);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const isPollingRef = useRef(false);

  const checkSession = useCallback(async () => {
    // Prevent concurrent polling
    if (isPollingRef.current) return;

    isPollingRef.current = true;

    try {
      const { isAuthenticated: stillAuthenticated } = await authApi.status();

      if (!stillAuthenticated) {
        // Session expired - the API client will handle redirect
        // This is a fallback check
        const authState = useAuthStore.getState();
        if (authState.isAuthenticated) {
          authState.clearAuth();
          if (typeof window !== "undefined") {
            window.location.href = "/login?session_expired=true";
          }
        }
      }
    } catch {
      // Network error - don't log out, just skip this check
      console.warn("Session check failed - network error");
    } finally {
      isPollingRef.current = false;
    }
  }, []);

  useEffect(() => {
    // Don't start polling until initialized and authenticated
    if (!enabled || !isInitialized || !isAuthenticated) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Start polling
    intervalRef.current = setInterval(checkSession, interval);

    // Handle visibility change - pause polling when tab is hidden
    const handleVisibilityChange = () => {
      if (document.hidden) {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } else {
        // Tab became visible - check immediately and restart polling
        checkSession();
        intervalRef.current = setInterval(checkSession, interval);
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [enabled, isInitialized, isAuthenticated, interval, checkSession]);

  return { checkSession };
}

export default useSessionPolling;
