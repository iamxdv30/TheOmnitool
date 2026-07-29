/**
 * Unit tests for CSRF token management
 * Phase 3 - Frontend Authentication & State Management
 */

import {
  getCsrfToken,
  clearCsrfToken,
  hasCsrfToken,
  refreshCsrfToken,
} from "@/lib/api/csrf";

// Mock fetch
const mockFetch = global.fetch as jest.Mock;

describe("CSRF Token Management", () => {
  beforeEach(() => {
    clearCsrfToken();
    mockFetch.mockReset();
  });

  describe("getCsrfToken", () => {
    it("should fetch token from server on first call", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: { csrfToken: "test-token-123" } }),
      });

      const token = await getCsrfToken();

      expect(token).toBe("test-token-123");
      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(mockFetch).toHaveBeenCalledWith("/api/v1/auth/csrf", {
        credentials: "include",
      });
    });

    it("should return cached token on subsequent calls", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: { csrfToken: "cached-token" } }),
      });

      await getCsrfToken();
      await getCsrfToken();
      await getCsrfToken();

      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it("should throw error when fetch fails", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(getCsrfToken()).rejects.toThrow("Failed to fetch CSRF token");
    });

    it("should throw error when token not in response", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: {} }),
      });

      await expect(getCsrfToken()).rejects.toThrow("CSRF token not found in response");
    });
  });

  describe("clearCsrfToken", () => {
    it("should clear cached token", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: { csrfToken: "token" } }),
      });

      await getCsrfToken();
      expect(hasCsrfToken()).toBe(true);

      clearCsrfToken();
      expect(hasCsrfToken()).toBe(false);
    });
  });

  describe("hasCsrfToken", () => {
    it("should return false when no token cached", () => {
      expect(hasCsrfToken()).toBe(false);
    });

    it("should return true when token is cached", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: { csrfToken: "token" } }),
      });

      await getCsrfToken();
      expect(hasCsrfToken()).toBe(true);
    });
  });

  describe("refreshCsrfToken", () => {
    it("should clear and fetch new token", async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ data: { csrfToken: "old-token" } }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ data: { csrfToken: "new-token" } }),
        });

      const oldToken = await getCsrfToken();
      expect(oldToken).toBe("old-token");

      const newToken = await refreshCsrfToken();
      expect(newToken).toBe("new-token");
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });
});
