import Link from "next/link";
import { Button } from "@/components/ui";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-surface-900">
      <main className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center text-center p-4">
        <h2 className="font-display text-4xl font-bold text-primary-glow mb-4">404</h2>
        <h3 className="text-2xl font-semibold text-text-high mb-4">Page Not Found</h3>
        <p className="text-text-muted max-w-md mb-8">
          The page you are looking for does not exist or has been moved.
        </p>
        <Link href="/">
          <Button variant="glow">Return Home</Button>
        </Link>
      </main>
    </div>
  );
}
