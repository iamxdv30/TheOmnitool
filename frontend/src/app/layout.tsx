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
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var storageKey = 'omnitool-ui';
                  var stored = localStorage.getItem(storageKey);
                  var theme = 'dark';
                  
                  if (stored) {
                    var parsed = JSON.parse(stored);
                    if (parsed.state && parsed.state.theme) {
                      theme = parsed.state.theme;
                    }
                  }
                  
                  if (theme === 'dark') {
                    document.documentElement.classList.add('dark');
                    document.documentElement.classList.remove('light');
                  } else {
                    document.documentElement.classList.add('light');
                    document.documentElement.classList.remove('dark');
                  }
                } catch (e) {}
              })()
            `,
          }}
        />
      </head>
      <body
        className={`${spaceGrotesk.variable} ${inter.variable} antialiased bg-surface-900 text-text-high`}
      >
        {/* Global 3D Canvas for View Tunneling */}
        <CanvasProvider />

        {/* Header */}
        <Header />

        {/* Main Content */}
        <main className="relative z-10 pt-16">{children}</main>

        {/* Toast Notifications */}
        <Toaster />
      </body>
    </html>
  );
}
