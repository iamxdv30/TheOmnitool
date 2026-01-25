/**
 * Unit tests for authStore
 * Phase 3 - Frontend Authentication & State Management
 */

import { useAuthStore, getAuthState } from "@/store/authStore";

// Mock user data
const mockUser = {
  id: 1,
  username: "testuser",
  email: "test@example.com",
  role: "user" as const,
  email_verified: true,
  created_at: "2024-01-01T00:00:00Z",
};

describe("authStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      isInitialized: false,
      permissions: [],
      error: null,
    });
  });

  describe("initial state", () => {
    it("should have correct initial state", () => {
      const state = getAuthState();

      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(true);
      expect(state.isInitialized).toBe(false);
      expect(state.permissions).toEqual([]);
      expect(state.error).toBeNull();
    });
  });

  describe("setUser", () => {
    it("should set user and update isAuthenticated to true", () => {
      getAuthState().setUser(mockUser);

      const state = getAuthState();
      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
      expect(state.error).toBeNull();
    });

    it("should clear user and set isAuthenticated to false when passed null", () => {
      // First set a user
      getAuthState().setUser(mockUser);
      expect(getAuthState().isAuthenticated).toBe(true);

      // Then clear
      getAuthState().setUser(null);

      const state = getAuthState();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe("setLoading", () => {
    it("should update isLoading state", () => {
      getAuthState().setLoading(false);
      expect(getAuthState().isLoading).toBe(false);

      getAuthState().setLoading(true);
      expect(getAuthState().isLoading).toBe(true);
    });
  });

  describe("setError", () => {
    it("should set error message", () => {
      getAuthState().setError("Test error");
      expect(getAuthState().error).toBe("Test error");
    });

    it("should clear error when passed null", () => {
      getAuthState().setError("Test error");
      getAuthState().setError(null);
      expect(getAuthState().error).toBeNull();
    });
  });

  describe("setPermissions", () => {
    it("should update permissions array", () => {
      const permissions = ["tool1", "tool2", "tool3"];
      getAuthState().setPermissions(permissions);
      expect(getAuthState().permissions).toEqual(permissions);
    });
  });

  describe("clearAuth", () => {
    it("should reset auth state while preserving loading states", () => {
      // Set up authenticated state
      getAuthState().setUser(mockUser);
      getAuthState().setPermissions(["tool1"]);
      getAuthState().setError("some error");

      // Clear auth
      getAuthState().clearAuth();

      const state = getAuthState();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.permissions).toEqual([]);
      expect(state.error).toBeNull();
    });
  });

  describe("setInitialized", () => {
    it("should update isInitialized state", () => {
      expect(getAuthState().isInitialized).toBe(false);

      getAuthState().setInitialized(true);
      expect(getAuthState().isInitialized).toBe(true);
    });
  });
});
