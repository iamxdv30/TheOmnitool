"use client";

import { View } from "@react-three/drei";
import { useRef } from "react";
import { Scene } from "./Scene";

interface SceneViewProps {
  className?: string;
}

/**
 * SceneView component for View Tunneling
 *
 * Place this component anywhere in your HTML flow to render
 * 3D content at that position while using the global Canvas context.
 *
 * Benefits:
 * - Perfect scroll syncing
 * - Correct z-indexing with DOM
 * - Single WebGL context (low memory usage)
 */
export function SceneView({ className }: SceneViewProps) {
  const viewRef = useRef<HTMLDivElement>(null!);

  return (
    <div
      ref={viewRef}
      className={`relative ${className || ""}`}
      style={{ touchAction: "pan-y" }}
    >
      <View track={viewRef}>
        <Scene />
      </View>
    </div>
  );
}

export default SceneView;
