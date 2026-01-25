/**
 * Auth API endpoints
 * Based on Phase 3 spec (Section 3.4)
 */

import { apiClient, isSuccess } from "./client";
import { clearCsrfToken } from "./csrf";
import { getAuthState } from "@/store/authStore";
import type { User, LoginCredentials, RegisterCredentials } from "@/types";

/**
 * Auth status response
 */
interface AuthStatusResponse {
  isAuthenticated: boolean;
  user: User | null;
}

/**
 * Login response
 */
interface LoginResponse {
  user: User;
}

/**
 * Register response
 */
interface RegisterResponse {
  requires_verification: boolean;
  message?: string;
}

/**
 * Auth API methods
 */
export const authApi = {
  /**
   * Check current authentication status
   * GET /api/v1/auth/status
   */
  async status(): Promise<AuthStatusResponse> {
    const response = await apiClient.get<AuthStatusResponse>("/auth/status", {
      skipAuth: true, // Don't redirect on 401 for status check
    });

    if (isSuccess(response)) {
      return response.data;
    }

    return { isAuthenticated: false, user: null };
  },

  /**
   * Login with credentials
   * POST /api/v1/auth/login
   */
  async login(credentials: LoginCredentials): Promise<{
    success: boolean;
    user?: User;
    error?: string;
    errorCode?: string;
  }> {
    const response = await apiClient.post<LoginResponse>("/auth/login", credentials, {
      skipAuth: true, // Handle auth errors manually
    });

    if (isSuccess(response)) {
      const { user } = response.data;
      getAuthState().setUser(user);
      return { success: true, user };
    }

    return {
      success: false,
      error: response.message,
      errorCode: response.error_code,
    };
  },

  /**
   * Logout current user
   * POST /api/v1/auth/logout
   */
  async logout(): Promise<void> {
    await apiClient.post("/auth/logout");
    getAuthState().clearAuth();
    clearCsrfToken();
  },

  /**
   * Register new user
   * POST /api/v1/auth/register
   */
  async register(credentials: RegisterCredentials): Promise<{
    success: boolean;
    requiresVerification?: boolean;
    error?: string;
  }> {
    const response = await apiClient.post<RegisterResponse>("/auth/register", {
      name: credentials.name,
      username: credentials.username,
      email: credentials.email,
      password: credentials.password,
    });

    if (isSuccess(response)) {
      return {
        success: true,
        requiresVerification: response.data.requires_verification ?? true,
      };
    }

    return {
      success: false,
      error: response.message,
    };
  },

  /**
   * Request password reset email
   * POST /api/v1/auth/forgot-password
   */
  async forgotPassword(email: string, recaptchaToken?: string): Promise<{
    success: boolean;
    error?: string;
  }> {
    const response = await apiClient.post("/auth/forgot-password", {
      email,
      recaptcha_token: recaptchaToken,
    });

    if (isSuccess(response)) {
      return { success: true };
    }

    return { success: false, error: response.message };
  },

  /**
   * Reset password with token
   * POST /api/v1/auth/reset-password
   */
  async resetPassword(token: string, newPassword: string): Promise<{
    success: boolean;
    error?: string;
  }> {
    const response = await apiClient.post("/auth/reset-password", {
      token,
      new_password: newPassword,
    });

    if (isSuccess(response)) {
      return { success: true };
    }

    return { success: false, error: response.message };
  },

  /**
   * Resend verification email
   * POST /api/v1/auth/resend-verification
   */
  async resendVerification(email: string, recaptchaToken?: string): Promise<{
    success: boolean;
    error?: string;
  }> {
    const response = await apiClient.post("/auth/resend-verification", {
      email,
      recaptcha_token: recaptchaToken,
    });

    if (isSuccess(response)) {
      return { success: true };
    }

    return { success: false, error: response.message };
  },

  /**
   * Initialize auth state on app load
   * Checks session and updates store
   */
  async initialize(): Promise<void> {
    const authState = getAuthState();

    try {
      authState.setLoading(true);
      const { isAuthenticated, user } = await this.status();

      if (isAuthenticated && user) {
        authState.setUser(user);
      } else {
        authState.clearAuth();
      }
    } catch {
      authState.clearAuth();
    } finally {
      authState.setLoading(false);
      authState.setInitialized(true);
    }
  },
};

export default authApi;
