"use client";

import { useState, useEffect, useCallback } from "react";
import type { User, ApiResponse, LoginCredentials, RegisterCredentials } from "@/types";

interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<{ success: boolean; requiresVerification?: boolean }>;
  forgotPassword: (email: string) => Promise<boolean>;
  resetPassword: (token: string, password: string) => Promise<boolean>;
  resendVerification: (email: string) => Promise<boolean>;
  clearError: () => void;
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkAuth = useCallback(async () => {
    try {
      setIsLoading(true);
      const res = await fetch("/api/auth/me", {
        credentials: "include",
      });

      if (res.ok) {
        const data: ApiResponse<{ user: User }> = await res.json();
        if (data.status === "success" && data.data?.user) {
          setUser(data.data.user);
        } else {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = useCallback(
    async (credentials: LoginCredentials): Promise<boolean> => {
      try {
        setIsLoading(true);
        setError(null);

        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(credentials),
        });

        const data: ApiResponse<{ user: User }> = await res.json();

        if (data.status === "success" && data.data?.user) {
          setUser(data.data.user);
          return true;
        } else {
          setError(data.message || "Login failed");
          return false;
        }
      } catch {
        setError("Network error. Please try again.");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const logout = useCallback(async () => {
    try {
      setIsLoading(true);
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
      setUser(null);
    } catch {
      // Still clear user on error
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(
    async (
      credentials: RegisterCredentials
    ): Promise<{ success: boolean; requiresVerification?: boolean }> => {
      try {
        setIsLoading(true);
        setError(null);

        const res = await fetch("/api/auth/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            name: credentials.name,
            username: credentials.username,
            email: credentials.email,
            password: credentials.password,
          }),
        });

        const data: ApiResponse<{ requires_verification?: boolean }> =
          await res.json();

        if (data.status === "success") {
          return {
            success: true,
            requiresVerification: data.data?.requires_verification ?? true,
          };
        } else {
          setError(data.message || "Registration failed");
          return { success: false };
        }
      } catch {
        setError("Network error. Please try again.");
        return { success: false };
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const forgotPassword = useCallback(async (email: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);

      const res = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ email }),
      });

      const data: ApiResponse = await res.json();

      if (data.status === "success") {
        return true;
      } else {
        setError(data.message || "Failed to send reset email");
        return false;
      }
    } catch {
      setError("Network error. Please try again.");
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resetPassword = useCallback(
    async (token: string, password: string): Promise<boolean> => {
      try {
        setIsLoading(true);
        setError(null);

        const res = await fetch(`/api/auth/reset-password/${token}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ password }),
        });

        const data: ApiResponse = await res.json();

        if (data.status === "success") {
          return true;
        } else {
          setError(data.message || "Failed to reset password");
          return false;
        }
      } catch {
        setError("Network error. Please try again.");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const resendVerification = useCallback(
    async (email: string): Promise<boolean> => {
      try {
        setIsLoading(true);
        setError(null);

        const res = await fetch("/api/auth/resend-verification", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ email }),
        });

        const data: ApiResponse = await res.json();

        if (data.status === "success") {
          return true;
        } else {
          setError(data.message || "Failed to resend verification email");
          return false;
        }
      } catch {
        setError("Network error. Please try again.");
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
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
