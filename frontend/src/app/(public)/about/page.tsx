"use client";

import { Card, CardContent } from "@/components/ui";
import { Sparkles, Zap, Heart, Rocket } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";

const sections = [
  {
    id: "story",
    title: "Our Story",
    icon: Sparkles,
    content:
      "Hey there! Ever find yourself hopping between different sites for simple things like a Unix timestamp converter or wishing you had Email Templates at your fingertips? That's exactly why I created OmniTools! It started as my own little project to make my documentation work a breeze, but I soon realized lots of folks could use a handy, all-in-one spot for these everyday helpers – tools designed with genuine usefulness and simplicity in mind.",
  },
  {
    id: "what-is-omnitool",
    title: "What is OmniTool?",
    icon: Zap,
    content:
      "So, OmniTools is now your friendly, cloud-based hub for just that. It's built with Flask, lives on Heroku, and Cloudflare keeps things running smoothly and securely. And here's something I'm really excited about: OmniTools is completely free to use and has absolutely no ads!",
  },
  {
    id: "philosophy",
    title: "Our Philosophy & Future",
    icon: Heart,
    content:
      "The best part (besides that!) is that it's always growing. I'm actively cooking up more awesome, free tools to add to the collection. My goal is to make OmniTools your absolute go-to for saving time and making your workflow a whole lot smoother, without any distractions.",
  },
  {
    id: "join-us",
    title: "Join the Journey",
    icon: Rocket,
    content:
      "Why not dive in and try them out? I'm building OmniTools for people like you, and your feedback or suggestions for new tools would be amazing as it continues to evolve. Stay tuned for what's next!",
  },
];

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <div className="mb-16 text-center">
        <h1 className="font-display text-4xl font-bold text-text-high sm:text-5xl">
          About <span className="text-primary">OmniTool</span>
        </h1>
        <p className="mt-4 text-lg text-text-muted">
          Your all-in-one productivity toolkit, built with love.
        </p>
      </div>

      {/* Content Sections */}
      <div className="space-y-8">
        {sections.map((section, index) => {
          const Icon = section.icon;
          return (
            <Card
              key={section.id}
              className={`transition-all hover:border-primary/30 ${
                index % 2 === 0 ? "" : "md:ml-8"
              }`}
            >
              <CardContent className="p-6 sm:p-8">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/20">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h2 className="font-display text-xl font-semibold text-text-high sm:text-2xl">
                      {section.title}
                    </h2>
                    <p className="mt-3 leading-relaxed text-text-muted">
                      {section.content}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* CTA Section */}
      <div className="mt-16 text-center">
        <Card variant="glass" className="inline-block">
          <CardContent className="p-8">
            <h3 className="font-display text-2xl font-semibold text-text-high">
              Ready to get started?
            </h3>
            <p className="mt-2 text-text-muted">
              Create a free account and explore our tools today.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
              <Link href="/register">
                <Button size="lg">Get Started Free</Button>
              </Link>
              <Link href="/contact">
                <Button variant="outline" size="lg">
                  Contact Us
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
