"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import {
  Environment,
  Float,
  MeshDistortMaterial,
} from "@react-three/drei";
import { Mesh } from "three";

/**
 * Demo scene with floating geometric shapes
 * Replace this with actual 3D content as needed
 */
export function Scene() {
  return (
    <>
      {/* Ambient and directional lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1} color="#A3B18A" />
      <pointLight position={[-10, -10, -5]} intensity={0.5} color="#577A81" />

      {/* Floating geometric shapes */}
      <Float
        speed={2}
        rotationIntensity={0.5}
        floatIntensity={0.5}
        floatingRange={[-0.1, 0.1]}
      >
        <FloatingShape position={[0, 0, 0]} />
      </Float>

      <Float
        speed={1.5}
        rotationIntensity={0.3}
        floatIntensity={0.3}
        floatingRange={[-0.05, 0.05]}
      >
        <FloatingShape position={[-2, 1, -2]} scale={0.5} color="#9CDFB9" />
      </Float>

      <Float
        speed={1.8}
        rotationIntensity={0.4}
        floatIntensity={0.4}
        floatingRange={[-0.08, 0.08]}
      >
        <FloatingShape position={[2, -1, -1]} scale={0.7} color="#577A81" />
      </Float>

      {/* Environment for reflections */}
      <Environment preset="night" />
    </>
  );
}

interface FloatingShapeProps {
  position?: [number, number, number];
  scale?: number;
  color?: string;
}

function FloatingShape({
  position = [0, 0, 0],
  scale = 1,
  color = "#588157",
}: FloatingShapeProps) {
  const meshRef = useRef<Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.2;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3;
    }
  });

  return (
    <mesh ref={meshRef} position={position} scale={scale}>
      <icosahedronGeometry args={[1, 1]} />
      <MeshDistortMaterial
        color={color}
        speed={2}
        distort={0.3}
        roughness={0.4}
        metalness={0.8}
      />
    </mesh>
  );
}

export default Scene;
