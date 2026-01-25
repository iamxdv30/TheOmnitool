import { create } from "zustand";
import { subscribeWithSelector, persist } from "zustand/middleware";
import type { User } from "@/types";

/**
 * Auth State Interface
 * Based on Phase 3 spec (Section 4.1)
 */
interface AuthState {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  permissions: string[]; // Tool access list
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setPermissions: (permissions: string[]) => void;
  clearAuth: () => void;
  setInitialized: (initialized: boolean) => void;
}

/**
 * Initial state for reset operations
 */
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  isInitialized: false,
  permissions: [],
  error: null,
};

/**
 * Zustand Auth Store
 * 
 * Manages authentication state globally across the application.
 * Uses subscribeWithSelector for efficient component subscriptions.
 * Uses persist middleware to maintain state across page refreshes (user info only).
 */
export const useAuthStore = create<AuthState>()(
  subscribeWithSelector(
    persist(
      (set) => ({
        ...initialState,

        setUser: (user) =>
          set({
            user,
            isAuthenticated: !!user,
            error: null,
          }),

        setLoading: (isLoading) => set({ isLoading }),

        setError: (error) => set({ error }),

        setPermissions: (permissions) => set({ permissions }),

        setInitialized: (isInitialized) => set({ isInitialized }),

        clearAuth: () =>
          set({
            user: null,
            isAuthenticated: false,
            permissions: [],
            error: null,
          }),
      }),
      {
        name: "omnitool-auth",
        // Only persist user data, not loading states
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          permissions: state.permissions,
        }),
      }
    )
  )
);

/**
 * Selector hooks for performance optimization
 * Use these instead of accessing the full store to minimize re-renders
 */
export const useUser = () => useAuthStore((state) => state.user);
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated);
export const useAuthLoading = () => useAuthStore((state) => state.isLoading);
export const useAuthError = () => useAuthStore((state) => state.error);
export const usePermissions = () => useAuthStore((state) => state.permissions);
export const useIsInitialized = () => useAuthStore((state) => state.isInitialized);

/**
 * Check if user has permission to access a specific tool
 */
export const useHasPermission = (toolName: string) =>
  useAuthStore((state) => state.permissions.includes(toolName));

/**
 * Check if user has a specific role
 */
export const useHasRole = (role: "user" | "admin" | "superadmin") =>
  useAuthStore((state) => {
    if (!state.user) return false;
    if (role === "user") return true;
    if (role === "admin") return state.user.role === "admin" || state.user.role === "superadmin";
    return state.user.role === "superadmin";
  });

/**
 * Get auth store state outside of React components
 * Useful for API interceptors and middleware
 */
export const getAuthState = () => useAuthStore.getState();

/**
 * Subscribe to auth state changes outside of React
 * Returns unsubscribe function
 */
export const subscribeToAuth = (callback: (state: AuthState) => void) =>
  useAuthStore.subscribe(callback);
