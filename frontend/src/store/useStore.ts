import { create } from "zustand";
import { subscribeWithSelector, persist } from "zustand/middleware";

interface AppState {
  // Performance state
  dpr: number;
  setDpr: (dpr: number) => void;

  // UI state
  isMobile: boolean;
  setIsMobile: (isMobile: boolean) => void;

  // 3D scene state
  isSceneReady: boolean;
  setSceneReady: (ready: boolean) => void;

  // Performance monitoring
  fps: number;
  setFps: (fps: number) => void;

  // Theme state (for future use)
  theme: "dark" | "light";
  setTheme: (theme: "dark" | "light") => void;
}

export const useStore = create<AppState>()(
  subscribeWithSelector(
    persist(
      (set) => ({
        // Performance state - start with lower DPR for mobile
        dpr: 1.5,
        setDpr: (dpr) => set({ dpr }),

        // UI state
        isMobile: false,
        setIsMobile: (isMobile) => set({ isMobile }),

        // 3D scene state
        isSceneReady: false,
        setSceneReady: (isSceneReady) => set({ isSceneReady }),

        // Performance monitoring
        fps: 60,
        setFps: (fps) => set({ fps }),

        // Theme (always dark for this design)
        theme: "dark",
        setTheme: (theme) => set({ theme }),
      }),
      {
        name: "omnitool-ui",
        partialize: (state) => ({ theme: state.theme }),
      }
    )
  )
);

// Selector hooks for performance
export const useDpr = () => useStore((state) => state.dpr);
export const useIsMobile = () => useStore((state) => state.isMobile);
export const useIsSceneReady = () => useStore((state) => state.isSceneReady);
export const useFps = () => useStore((state) => state.fps);
export const useTheme = () => useStore((state) => state.theme);
export const useSetTheme = () => useStore((state) => state.setTheme);
