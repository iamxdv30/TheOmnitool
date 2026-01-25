import { create } from "zustand";
import { subscribeWithSelector } from "zustand/middleware";
import { toast as sonnerToast } from "sonner";

/**
 * Toast notification types
 */
export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  title?: string;
  duration?: number; // ms, default 5000
  dismissible?: boolean;
}

/**
 * Modal configuration
 */
export interface ModalConfig {
  id: string;
  title?: string;
  content?: React.ReactNode;
  onConfirm?: () => void | Promise<void>;
  onCancel?: () => void;
  confirmText?: string;
  cancelText?: string;
  variant?: "default" | "danger";
}

/**
 * UI State Interface
 */
interface UIState {
  // Toast state
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;

  // Modal state
  activeModal: ModalConfig | null;
  openModal: (config: ModalConfig) => void;
  closeModal: () => void;

  // Loading overlay (for global loading states)
  isGlobalLoading: boolean;
  globalLoadingMessage: string | null;
  setGlobalLoading: (loading: boolean, message?: string) => void;

  // Sidebar state (for dashboard)
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  isSidebarCollapsed: boolean;
  toggleSidebarCollapsed: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

/**
 * Generate unique ID for toasts
 */
const generateId = () => `toast-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

/**
 * Zustand UI Store
 * 
 * Manages UI state globally: toasts, modals, loading states, sidebar
 */
export const useUIStore = create<UIState>()(
  subscribeWithSelector((set, get) => ({
    // Toast state
    toasts: [],

    addToast: (toast) => {
      const id = generateId();
      const newToast: Toast = {
        id,
        duration: 5000,
        dismissible: true,
        ...toast,
      };

      set((state) => ({
        toasts: [...state.toasts, newToast],
      }));

      // Auto-remove after duration
      if (newToast.duration && newToast.duration > 0) {
        setTimeout(() => {
          get().removeToast(id);
        }, newToast.duration);
      }

      return id;
    },

    removeToast: (id) =>
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      })),

    clearToasts: () => set({ toasts: [] }),

    // Modal state
    activeModal: null,

    openModal: (config) => set({ activeModal: config }),

    closeModal: () => set({ activeModal: null }),

    // Global loading
    isGlobalLoading: false,
    globalLoadingMessage: null,

    setGlobalLoading: (loading, message) =>
      set({
        isGlobalLoading: loading,
        globalLoadingMessage: message ?? null,
      }),

    // Sidebar
    isSidebarOpen: true,

    toggleSidebar: () =>
      set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

    setSidebarOpen: (open) => set({ isSidebarOpen: open }),

    // Sidebar Collapsed (Desktop)
    isSidebarCollapsed: false,

    toggleSidebarCollapsed: () =>
      set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),

    setSidebarCollapsed: (collapsed) => set({ isSidebarCollapsed: collapsed }),
  }))
);

/**
 * Convenience functions for common toast types
 * These now use Sonner directly for better compatibility
 */
export const toast = {
  success: (message: string, title?: string) => {
    if (title) {
      sonnerToast.success(`${title}: ${message}`);
    } else {
      sonnerToast.success(message);
    }
  },

  error: (message: string | { message?: string }, title?: string) => {
    // Ensure message is always a string
    const errorMessage = typeof message === 'string' ? message : 
                        message?.message || 'An error occurred';
    if (title) {
      sonnerToast.error(`${title}: ${errorMessage}`);
    } else {
      sonnerToast.error(errorMessage);
    }
  },

  warning: (message: string, title?: string) => {
    if (title) {
      sonnerToast.warning(`${title}: ${message}`);
    } else {
      sonnerToast.warning(message);
    }
  },

  info: (message: string, title?: string) => {
    if (title) {
      sonnerToast.info(`${title}: ${message}`);
    } else {
      sonnerToast.info(message);
    }
  },
};

/**
 * Selector hooks
 */
export const useToasts = () => useUIStore((state) => state.toasts);
export const useActiveModal = () => useUIStore((state) => state.activeModal);
export const useIsGlobalLoading = () => useUIStore((state) => state.isGlobalLoading);
export const useGlobalLoadingMessage = () => useUIStore((state) => state.globalLoadingMessage);
export const useIsSidebarOpen = () => useUIStore((state) => state.isSidebarOpen);

/**
 * Get UI store state outside of React components
 */
export const getUIState = () => useUIStore.getState();
