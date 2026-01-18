"use client";

import dynamic from "next/dynamic";

/**
 * Dynamically imported Canvas with SSR disabled
 * This is critical for performance - the 3D canvas should not
 * block initial page load or hydration
 */
const Canvas = dynamic(
  () => import("@/components/canvas/Canvas").then((mod) => mod.Canvas),
  {
    ssr: false,
    loading: () => null,
  }
);

interface CanvasProviderProps {
  children?: React.ReactNode;
}

export function CanvasProvider({ children }: CanvasProviderProps) {
  return <Canvas>{children}</Canvas>;
}

export default CanvasProvider;
