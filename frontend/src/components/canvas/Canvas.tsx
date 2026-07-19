"use client";

import { Canvas as ThreeCanvas } from "@react-three/fiber";
import { Preload, View, PerformanceMonitor } from "@react-three/drei";
import { Suspense, useRef, useEffect } from "react";
import { useStore } from "@/store/useStore";

interface CanvasProps {
  children?: React.ReactNode;
}

/**
 * Global Canvas component for View Tunneling architecture
 *
 * This canvas sits at the root layout and uses View components
 * to render 3D content into specific DOM elements while maintaining
 * a single WebGL context.
 */
export function Canvas({ children }: CanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { dpr, setDpr, setIsMobile, setSceneReady, setFps } = useStore();

  useEffect(() => {
    // Detect mobile device
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);

    return () => window.removeEventListener("resize", checkMobile);
  }, [setIsMobile]);

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
    >
      <ThreeCanvas
        dpr={dpr}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
        }}
        camera={{ position: [0, 0, 5], fov: 45 }}
        onCreated={() => setSceneReady(true)}
        style={{ pointerEvents: "none" }}
        frameloop="demand"
      >
        <Suspense fallback={null}>
          <PerformanceMonitor
            onIncline={() => setDpr(Math.min(dpr + 0.5, 2))}
            onDecline={() => setDpr(Math.max(dpr - 0.5, 1))}
            onChange={({ fps }) => setFps(fps)}
            flipflops={3}
            bounds={(refreshRate) => [40, refreshRate]}
          >
            {/* View.Port renders all tracked View components */}
            <View.Port />
            {children}
          </PerformanceMonitor>
          <Preload all />
        </Suspense>
      </ThreeCanvas>
    </div>
  );
}

export default Canvas;
