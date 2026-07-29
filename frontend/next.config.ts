import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable React strict mode for better development experience
  reactStrictMode: true,

  // Optimize images
  images: {
    formats: ["image/avif", "image/webp"],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
  },

  // Experimental features for better performance
  experimental: {
    // Enable optimized package imports
    optimizePackageImports: ["lucide-react", "@react-three/drei"],
  },

  // Turbopack configuration (Next.js 16+ default)
  turbopack: {
    // Resolve aliases for better module resolution
    resolveAlias: {
      // Add any custom aliases here if needed
    },
  },

  // Configure transpilation for 3D packages
  transpilePackages: [
    "three",
    "@react-three/fiber",
    "@react-three/drei",
    "@react-three/rapier",
  ],

  // Proxy rewrites to Flask backend (running on port 5000 on the dyno)
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:5000/api/:path*",
      },
      {
        source: "/health/:path*",
        destination: "http://127.0.0.1:5000/health/:path*",
      },
    ];
  },
};

export default nextConfig;
