/**
 * CSRF Token Management
 * Based on Phase 3 spec (Section 4.5)
 * 
 * - Fetches CSRF token from Flask backend
 * - Caches token for subsequent requests
 * - Clears token on logout
 */

let csrfToken: string | null = null;

/**
 * Get CSRF token, fetching from server if not cached
 */
export async function getCsrfToken(): Promise<string> {
  if (!csrfToken) {
    try {
      const response = await fetch("/api/v1/auth/csrf", {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch CSRF token");
      }

      const data = await response.json();
      csrfToken = data.data?.csrfToken || data.csrfToken;

      if (!csrfToken) {
        throw new Error("CSRF token not found in response");
      }
    } catch (error) {
      console.error("CSRF token fetch failed:", error);
      throw error;
    }
  }

  return csrfToken;
}

/**
 * Clear cached CSRF token (call on logout)
 */
export function clearCsrfToken(): void {
  csrfToken = null;
}

/**
 * Check if CSRF token is cached
 */
export function hasCsrfToken(): boolean {
  return csrfToken !== null;
}

/**
 * Force refresh CSRF token
 */
export async function refreshCsrfToken(): Promise<string> {
  csrfToken = null;
  return getCsrfToken();
}
