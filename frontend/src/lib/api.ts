/**
 * Type-safe API client for Flask backend
 * Uses the proxy configured in next.config.ts
 */

import type { ApiResponse } from "@/types";

const API_BASE = "/api/v1";

type RequestMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

interface RequestOptions extends Omit<RequestInit, "method" | "body"> {
  params?: Record<string, string | number | boolean>;
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
 * Generic fetch wrapper with type safety and error handling
 */
async function request<T>(
  method: RequestMethod,
  endpoint: string,
  data?: unknown,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const { params, headers: customHeaders, ...rest } = options;

  const url = buildUrl(endpoint, params);

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...customHeaders,
  };

  const config: RequestInit = {
    method,
    headers,
    credentials: "include", // Include session cookies
    ...rest,
  };

  if (data && method !== "GET") {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, config);

    // Handle unauthorized - redirect to login
    if (response.status === 401) {
      // Only redirect if we're in the browser
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return {
        status: "error",
        message: "Session expired. Please log in again.",
        error_code: "UNAUTHORIZED",
      };
    }

    // Handle no content responses
    if (response.status === 204) {
      return {
        status: "success",
        data: undefined as T,
      };
    }

    const json = await response.json();

    // Normalize response format
    if (response.ok) {
      return {
        status: "success",
        data: json.data ?? json,
        message: json.message,
      };
    }

    return {
      status: "error",
      message: json.message || json.error || "An error occurred",
      error_code: json.error_code,
    };
  } catch (error) {
    console.error("API request failed:", error);
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
export const api = {
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
export function isSuccess<T>(response: ApiResponse<T>): response is ApiResponse<T> & { status: "success"; data: T } {
  return response.status === "success" && response.data !== undefined;
}

/**
 * Check if response was an error
 */
export function isError<T>(response: ApiResponse<T>): response is ApiResponse<T> & { status: "error" } {
  return response.status === "error";
}

export default api;
