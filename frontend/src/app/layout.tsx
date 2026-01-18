import type { Metadata } from "next";
import { Space_Grotesk, Inter } from "next/font/google";
import "./globals.css";
import { CanvasProvider } from "@/components/providers";
import { Header } from "@/components/layout";
import { Toaster } from "@/components/feedback";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-display",
  subsets: ["latin"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-body",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "The Omnitool",
  description: "A high-performance utility toolkit with 3D visualization",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${spaceGrotesk.variable} ${inter.variable} antialiased bg-surface-900 text-text-high`}
      >
        {/* Global 3D Canvas for View Tunneling */}
        <CanvasProvider />

        {/* Header */}
        <Header />

        {/* Main Content */}
        <main className="relative z-10">{children}</main>

        {/* Toast Notifications */}
        <Toaster />
      </body>
    </html>
  );
}
