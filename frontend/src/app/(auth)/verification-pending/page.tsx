"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Alert,
} from "@/components/ui";
import { useAuth } from "@/hooks";
import { Mail, RefreshCw, ArrowLeft, CheckCircle } from "lucide-react";

function VerificationPendingContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "";
  const { resendVerification, isLoading, error, clearError } = useAuth();
  const [isResent, setIsResent] = useState(false);
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleResend = async () => {
    if (countdown > 0) return;
    clearError();

    const success = await resendVerification(email);
    if (success) {
      setIsResent(true);
      setCountdown(60); // 60 second cooldown
    }
  };

  return (
    <Card variant="glass" className="w-full max-w-md">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20">
          <Mail className="h-6 w-6 text-primary" />
        </div>
        <CardTitle className="text-2xl">Verify Your Email</CardTitle>
        <CardDescription>
          We&apos;ve sent a verification link to{" "}
          <span className="font-medium text-text-high">{email}</span>
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {error && <Alert variant="error">{error}</Alert>}

        {isResent && (
          <Alert variant="success">
            <CheckCircle className="h-4 w-4" />
            Verification email resent successfully!
          </Alert>
        )}

        <div className="space-y-3 text-sm text-text-muted">
          <p>
            Click the link in your email to verify your account. If you
            don&apos;t see it, check your spam folder.
          </p>
          <p>The verification link will expire in 1 hour.</p>
        </div>
      </CardContent>

      <CardFooter className="flex flex-col gap-4">
        <Button
          variant="outline"
          className="w-full"
          onClick={handleResend}
          disabled={isLoading || countdown > 0}
        >
          {isLoading ? (
            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          {countdown > 0
            ? `Resend in ${countdown}s`
            : "Resend verification email"}
        </Button>

        <Link
          href="/login"
          className="flex items-center justify-center gap-2 text-sm text-primary hover:text-primary-hover transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to sign in
        </Link>
      </CardFooter>
    </Card>
  );
}

export default function VerificationPendingPage() {
  return (
    <Suspense
      fallback={
        <Card variant="glass" className="w-full max-w-md">
          <CardContent className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-primary" />
          </CardContent>
        </Card>
      }
    >
      <VerificationPendingContent />
    </Suspense>
  );
}
