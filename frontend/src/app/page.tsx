"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui";
import { Footer } from "@/components/layout";
import { ArrowRight, Zap, Shield, Gauge } from "lucide-react";

// Dynamically import SceneView to avoid SSR issues
const SceneView = dynamic(
  () => import("@/components/canvas/SceneView").then((mod) => mod.SceneView),
  { ssr: false }
);

const features = [
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Optimized for performance with lazy loading and on-demand rendering.",
  },
  {
    icon: Shield,
    title: "Secure by Design",
    description: "Role-based access control and enterprise-grade security features.",
  },
  {
    icon: Gauge,
    title: "Real-time Analytics",
    description: "Monitor usage and performance with built-in analytics dashboard.",
  },
];

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-16">
        {/* 3D Background via View Tunneling */}
        <SceneView className="absolute inset-0 w-full h-full" />

        {/* Hero Content */}
        <div className="relative z-10 container mx-auto px-4 text-center">
          <h1 className="font-display text-4xl md:text-6xl lg:text-7xl font-bold mb-6">
            <span className="text-text-high">The </span>
            <span className="text-primary-glow">Omnitool</span>
          </h1>
          <p className="text-text-muted text-lg md:text-xl max-w-2xl mx-auto mb-8">
            A high-performance utility toolkit with 3D visualization.
            Built for speed, designed for the future.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button variant="glow" size="lg">
                Get Started
                <ArrowRight size={20} />
              </Button>
            </Link>
            <Link href="/about">
              <Button variant="outline" size="lg">
                About Us
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-surface-800/50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold text-text-high mb-4">
              Built for Performance
            </h2>
            <p className="text-text-muted max-w-2xl mx-auto">
              Every feature is designed with performance in mind, ensuring a smooth
              experience across all devices.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature) => (
              <Card key={feature.title} variant="interactive" padding="lg">
                <CardHeader>
                  <div className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center mb-4">
                    <feature.icon className="text-primary-glow" size={24} />
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="container mx-auto px-4">
          <Card variant="glass" padding="xl" className="text-center">
            <CardContent>
              <h2 className="font-display text-3xl md:text-4xl font-bold text-text-high mb-4">
                Ready to Get Started?
              </h2>
              <p className="text-text-muted max-w-xl mx-auto mb-8">
                Join thousands of users who trust The Omnitool for their daily tasks.
              </p>
              <Link href="/register">
                <Button variant="glow" size="lg">
                  Get Started
                  <ArrowRight size={20} />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </>
  );
}
