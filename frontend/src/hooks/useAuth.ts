"use client";

import { useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import authApi from "@/lib/api/auth";
import { toast } from "@/store/uiStore";
import type { User, LoginCredentials, RegisterCredentials } from "@/types";

interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
  permissions: string[];
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<{ success: boolean; requiresVerification?: boolean }>;
  forgotPassword: (email: string, recaptchaToken?: string) => Promise<boolean>;
  resetPassword: (token: string, password: string) => Promise<boolean>;
  resendVerification: (email: string, recaptchaToken?: string) => Promise<boolean>;
  clearError: () => void;
}

/**
 * Authentication hook that integrates with Zustand store and API client
 * Provides auth actions and state for React components
 */
export function useAuth(): UseAuthReturn {
  const router = useRouter();

  // Select state from Zustand store
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isLoading = useAuthStore((state) => state.isLoading);
  const isInitialized = useAuthStore((state) => state.isInitialized);
  const error = useAuthStore((state) => state.error);
  const permissions = useAuthStore((state) => state.permissions);
  const setError = useAuthStore((state) => state.setError);
  const setLoading = useAuthStore((state) => state.setLoading);

  // Initialize auth on first mount
  useEffect(() => {
    if (!isInitialized) {
      authApi.initialize();
    }
  }, [isInitialized]);

  const login = useCallback(
    async (credentials: LoginCredentials): Promise<boolean> => {
      setLoading(true);
      setError(null);

      const result = await authApi.login(credentials);

      setLoading(false);

      if (result.success) {
        toast.success("Welcome back!");
        return true;
      }

      // Handle AUTH_UNVERIFIED
      if (result.errorCode === "AUTH_UNVERIFIED") {
        router.push("/verification-pending");
        return false;
      }

      setError(result.error || "Login failed");
      return false;
    },
    [router, setError, setLoading]
  );

  const logout = useCallback(async () => {
    setLoading(true);
    await authApi.logout();
    setLoading(false);
    toast.info("You have been logged out");
    router.push("/login");
  }, [router, setLoading]);

  const checkAuth = useCallback(async () => {
    await authApi.initialize();
  }, []);

  const register = useCallback(
    async (
      credentials: RegisterCredentials
    ): Promise<{ success: boolean; requiresVerification?: boolean }> => {
      setLoading(true);
      setError(null);

      const result = await authApi.register(credentials);

      setLoading(false);

      if (result.success) {
        toast.success("Account created! Please check your email to verify.");
        return {
          success: true,
          requiresVerification: result.requiresVerification,
        };
      }

      setError(result.error || "Registration failed");
      return { success: false };
    },
    [setError, setLoading]
  );

  const forgotPassword = useCallback(
    async (email: string, recaptchaToken?: string): Promise<boolean> => {
      setLoading(true);
      setError(null);

      const result = await authApi.forgotPassword(email, recaptchaToken);

      setLoading(false);

      if (result.success) {
        toast.success("Password reset email sent. Please check your inbox.");
        return true;
      }

      setError(result.error || "Failed to send reset email");
      return false;
    },
    [setError, setLoading]
  );

  const resetPassword = useCallback(
    async (token: string, password: string): Promise<boolean> => {
      setLoading(true);
      setError(null);

      const result = await authApi.resetPassword(token, password);

      setLoading(false);

      if (result.success) {
        toast.success("Password reset successfully. Please log in.");
        return true;
      }

      setError(result.error || "Failed to reset password");
      return false;
    },
    [setError, setLoading]
  );

  const resendVerification = useCallback(
    async (email: string, recaptchaToken?: string): Promise<boolean> => {
      setLoading(true);
      setError(null);

      const result = await authApi.resendVerification(email, recaptchaToken);

      setLoading(false);

      if (result.success) {
        toast.success("Verification email sent. Please check your inbox.");
        return true;
      }

      setError(result.error || "Failed to resend verification email");
      return false;
    },
    [setError, setLoading]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  return {
    user,
    isAuthenticated,
    isLoading,
    isInitialized,
    error,
    permissions,
    login,
    logout,
    checkAuth,
    register,
    forgotPassword,
    resetPassword,
    resendVerification,
    clearError,
  };
}
