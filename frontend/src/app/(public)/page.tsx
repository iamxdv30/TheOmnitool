"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { Button, Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui";
import { Footer } from "@/components/layout";
import { ArrowRight, Wrench, Shield, LayoutDashboard } from "lucide-react";

// Dynamically import SceneView to avoid SSR issues
const SceneView = dynamic(
  () => import("@/components/canvas/SceneView").then((mod) => mod.SceneView),
  { ssr: false }
);

const features = [
  {
    icon: Wrench,
    title: "Everyday Tools",
    description:
      "Tax calculators for US, Canada, and VAT, a character counter, and reusable email templates — with more on the way.",
  },
  {
    icon: Shield,
    title: "Secure by Design",
    description:
      "Verified accounts, CSRF-protected requests, bcrypt-hashed passwords, and role-based access control.",
  },
  {
    icon: LayoutDashboard,
    title: "Your Tools, Organized",
    description:
      "Search, favorites synced across devices, and a recent-activity feed so you can pick up where you left off.",
  },
];

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-16">
        {/* 3D Background via View Tunneling */}
        <SceneView className="absolute inset-0 w-full h-full -z-10" />

        {/* Hero Content */}
        <div className="relative z-20 container mx-auto px-4 text-center">
          <h1 className="font-display text-4xl md:text-6xl lg:text-7xl font-bold mb-6">
            <span className="text-text-high">The </span>
            <span className="text-primary-glow">Omnitool</span>
          </h1>
          <p className="text-text-muted text-lg md:text-xl max-w-2xl mx-auto mb-8">
            Simple tools, smarter workflows. Tax calculators, email templates,
            and everyday utilities — free, in one place.
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
              Why The Omnitool
            </h2>
            <p className="text-text-muted max-w-2xl mx-auto">
              Everyday utilities in one place, so you stop hopping between
              ten different single-purpose sites.
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
                Free to use, no ads, no distractions — built by a support engineer, for people who just want the tool to work.
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
