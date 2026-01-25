/**
 * Unit tests for uiStore
 * Phase 3 - Frontend Authentication & State Management
 */

import { useUIStore, toast, getUIState } from "@/store/uiStore";

describe("uiStore", () => {
  beforeEach(() => {
    // Reset store state before each test
    useUIStore.setState({
      toasts: [],
      activeModal: null,
      isGlobalLoading: false,
      globalLoadingMessage: null,
      isSidebarOpen: true,
    });
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe("toast system", () => {
    it("should add a toast with generated id", () => {
      const id = getUIState().addToast({
        type: "success",
        message: "Test message",
      });

      expect(id).toBeDefined();
      expect(getUIState().toasts).toHaveLength(1);
      expect(getUIState().toasts[0].message).toBe("Test message");
      expect(getUIState().toasts[0].type).toBe("success");
    });

    it("should remove toast by id", () => {
      const id = getUIState().addToast({
        type: "info",
        message: "Test",
      });

      expect(getUIState().toasts).toHaveLength(1);

      getUIState().removeToast(id);
      expect(getUIState().toasts).toHaveLength(0);
    });

    it("should auto-remove toast after duration", () => {
      getUIState().addToast({
        type: "success",
        message: "Auto remove",
        duration: 3000,
      });

      expect(getUIState().toasts).toHaveLength(1);

      // Fast-forward time
      jest.advanceTimersByTime(3000);

      expect(getUIState().toasts).toHaveLength(0);
    });

    it("should clear all toasts", () => {
      getUIState().addToast({ type: "success", message: "Toast 1" });
      getUIState().addToast({ type: "error", message: "Toast 2" });
      getUIState().addToast({ type: "warning", message: "Toast 3" });

      expect(getUIState().toasts).toHaveLength(3);

      getUIState().clearToasts();
      expect(getUIState().toasts).toHaveLength(0);
    });
  });

  describe("toast convenience functions", () => {
    it("toast.success should add success toast", () => {
      toast.success("Success message", "Title");

      const toasts = getUIState().toasts;
      expect(toasts).toHaveLength(1);
      expect(toasts[0].type).toBe("success");
      expect(toasts[0].message).toBe("Success message");
      expect(toasts[0].title).toBe("Title");
    });

    it("toast.error should add error toast with longer duration", () => {
      toast.error("Error message");

      const toasts = getUIState().toasts;
      expect(toasts).toHaveLength(1);
      expect(toasts[0].type).toBe("error");
      expect(toasts[0].duration).toBe(8000);
    });

    it("toast.warning should add warning toast", () => {
      toast.warning("Warning message");

      expect(getUIState().toasts[0].type).toBe("warning");
    });

    it("toast.info should add info toast", () => {
      toast.info("Info message");

      expect(getUIState().toasts[0].type).toBe("info");
    });
  });

  describe("modal system", () => {
    it("should open modal with config", () => {
      const modalConfig = {
        id: "test-modal",
        title: "Test Modal",
        confirmText: "OK",
      };

      getUIState().openModal(modalConfig);

      expect(getUIState().activeModal).toEqual(modalConfig);
    });

    it("should close modal", () => {
      getUIState().openModal({ id: "test" });
      expect(getUIState().activeModal).not.toBeNull();

      getUIState().closeModal();
      expect(getUIState().activeModal).toBeNull();
    });
  });

  describe("global loading", () => {
    it("should set global loading state", () => {
      getUIState().setGlobalLoading(true, "Loading...");

      expect(getUIState().isGlobalLoading).toBe(true);
      expect(getUIState().globalLoadingMessage).toBe("Loading...");
    });

    it("should clear loading message when disabled", () => {
      getUIState().setGlobalLoading(true, "Loading...");
      getUIState().setGlobalLoading(false);

      expect(getUIState().isGlobalLoading).toBe(false);
      expect(getUIState().globalLoadingMessage).toBeNull();
    });
  });

  describe("sidebar", () => {
    it("should toggle sidebar", () => {
      expect(getUIState().isSidebarOpen).toBe(true);

      getUIState().toggleSidebar();
      expect(getUIState().isSidebarOpen).toBe(false);

      getUIState().toggleSidebar();
      expect(getUIState().isSidebarOpen).toBe(true);
    });

    it("should set sidebar open state directly", () => {
      getUIState().setSidebarOpen(false);
      expect(getUIState().isSidebarOpen).toBe(false);

      getUIState().setSidebarOpen(true);
      expect(getUIState().isSidebarOpen).toBe(true);
    });
  });
});
