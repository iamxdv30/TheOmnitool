/**
 * API Client with interceptors
 * Based on Phase 3 spec (Section 4.2)
 * 
 * Features:
 * - Automatic CSRF token injection for mutating requests
 * - 401 handling: redirect to login
 * - 403 AUTH_UNVERIFIED handling: redirect to verification page
 * - Standardized response envelope
 */

import { getCsrfToken, clearCsrfToken } from "./csrf";
import { getAuthState } from "@/store/authStore";
import { toast } from "@/store/uiStore";
import type { ApiResponse } from "@/types";

const API_BASE = "/api/v1";

type RequestMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

interface RequestOptions extends Omit<RequestInit, "method" | "body"> {
  params?: Record<string, string | number | boolean>;
  skipAuth?: boolean; // Skip auth redirect on 401
  skipCsrf?: boolean; // Skip CSRF token injection
}

/**
 * Build URL with query parameters
 */
function buildUrl(endpoint: string, params?: Record<string, string | number | boolean>): string {
  const url = `${API_BASE}${endpoint}`;
  if (!params) return url;

  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    searchParams.append(key, String(value));
  });

  return `${url}?${searchParams.toString()}`;
}

/**
 * Handle response based on status code
 */
async function handleResponse<T>(
  response: Response,
  options: RequestOptions
): Promise<ApiResponse<T>> {
  // Handle 401 Unauthorized
  if (response.status === 401 && !options.skipAuth) {
    getAuthState().clearAuth();
    clearCsrfToken();

    if (typeof window !== "undefined") {
      window.location.href = "/login?session_expired=true";
    }

    return {
      status: "error",
      message: "Session expired. Please log in again.",
      error_code: "AUTH_REQUIRED",
    };
  }

  // Handle 403 Forbidden
  if (response.status === 403) {
    const data = await response.json();

    // Check for unverified email
    if (data.error?.code === "AUTH_UNVERIFIED" || data.error_code === "AUTH_UNVERIFIED") {
      if (typeof window !== "undefined") {
        window.location.href = "/verification-pending";
      }

      return {
        status: "error",
        message: "Please verify your email address.",
        error_code: "AUTH_UNVERIFIED",
      };
    }

    return {
      status: "error",
      message: data.message || data.error?.message || "Access denied",
      error_code: data.error_code || data.error?.code || "PERMISSION_DENIED",
    };
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {
      status: "success",
      data: undefined as T,
    };
  }

  // Parse JSON response
  const json = await response.json();

  // Helper function to extract error message from various response formats
  function extractErrorMessage(json: unknown): string {
    // Type guard to ensure we're working with an object
    if (!json || typeof json !== 'object') {
      return "An error occurred";
    }

    const jsonObj = json as Record<string, unknown>;
    
    // Handle success responses
    if (jsonObj.success !== false) {
      return typeof jsonObj.message === 'string' ? jsonObj.message : "";
    }

    // Handle other error responses
    const message = jsonObj.message || 
                    (jsonObj.error as Record<string, unknown>)?.message || 
                    jsonObj.error || 
                    "An error occurred";
    
    if (typeof message === 'string') {
      return message;
    }
    
    // If message is an object, try to extract the message property
    if (message && typeof message === 'object') {
      const msgObj = message as Record<string, unknown>;
      return typeof msgObj.message === 'string' ? msgObj.message : "An error occurred";
    }
    
    // Fallback to string representation
    return "An error occurred";
  }

  // Handle success responses
  if (response.ok) {
    return {
      status: "success",
      data: json.data ?? json,
      message: json.message,
    };
  }

  // Handle other error responses
  return {
    status: "error",
    message: extractErrorMessage(json),
    error_code: json.error_code || json.error?.code,
  };
}

/**
 * Generic fetch wrapper with type safety and interceptors
 */
async function request<T>(
  method: RequestMethod,
  endpoint: string,
  data?: unknown,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { params, headers: customHeaders, skipCsrf, ...rest } = options;

  const url = buildUrl(endpoint, params);

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...customHeaders,
  };

  // Inject CSRF token for mutating requests
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method) && !skipCsrf) {
    try {
      const csrfToken = await getCsrfToken();
      (headers as Record<string, string>)["X-CSRFToken"] = csrfToken;
    } catch {
      // Continue without CSRF token if fetch fails
      // Server will reject if CSRF is required
      console.warn("Could not fetch CSRF token");
    }
  }

  const config: RequestInit = {
    method,
    headers,
    credentials: "include",
    ...rest,
  };

  if (data && method !== "GET") {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, config);
    return handleResponse<T>(response, options);
  } catch (error) {
    console.error("API request failed:", error);

    toast.error("Network error. Please check your connection.");

    return {
      status: "error",
      message: "Network error. Please check your connection.",
      error_code: "NETWORK_ERROR",
    };
  }
}

/**
 * API client with typed methods
 */
export const apiClient = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>("GET", endpoint, undefined, options),

  post: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    request<T>("POST", endpoint, data, options),

  put: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    request<T>("PUT", endpoint, data, options),

  patch: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
    request<T>("PATCH", endpoint, data, options),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>("DELETE", endpoint, undefined, options),
};

/**
 * Check if response was successful
 */
export function isSuccess<T>(
  response: ApiResponse<T>
): response is ApiResponse<T> & { status: "success"; data: T } {
  return response.status === "success" && response.data !== undefined;
}

/**
 * Check if response was an error
 */
export function isError<T>(
  response: ApiResponse<T>
): response is ApiResponse<T> & { status: "error" } {
  return response.status === "error";
}

export default apiClient;
