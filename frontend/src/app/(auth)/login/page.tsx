"use client";

import { useState, useEffect, type FormEvent, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Input,
  Label,
  Alert,
} from "@/components/ui";
import { useAuth } from "@/hooks";
import { useTheme } from "@/store/useStore";
import { toast } from "@/store/uiStore";
import { Lock, User } from "lucide-react";
import ReCAPTCHA from "react-google-recaptcha";
import { useRef } from "react";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isLoading, error, clearError } = useAuth();
  const theme = useTheme();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [successMessage] = useState<string | null>(() => {
    // Initialize success message from URL params (runs once on mount)
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      if (params.get("password_reset") === "true") {
        return "Password reset successfully. Please log in with your new password.";
      }
      if (params.get("verified") === "true") {
        return "Email verified successfully! You can now log in.";
      }
    }
    return null;
  });
  const recaptchaRef = useRef<ReCAPTCHA>(null);
  const recaptchaSiteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;

  // Handle URL query params for session expiration, password reset, etc.
  useEffect(() => {
    const sessionExpired = searchParams.get("session_expired");
    const redirect = searchParams.get("redirect");

    if (sessionExpired === "true") {
      toast.warning("Your session has expired. Please log in again.");
    }

    // Store redirect URL for after login
    if (redirect) {
      sessionStorage.setItem("loginRedirect", redirect);
    }

    // Clear error state on mount
    clearError();
  }, [searchParams, clearError]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (!username || !password) {
      setLocalError("Please fill in all fields");
      return;
    }

    let recaptchaToken: string | undefined;
    if (recaptchaSiteKey && recaptchaRef.current) {
      recaptchaToken = recaptchaRef.current.getValue() || undefined;
      if (!recaptchaToken) {
        setLocalError("Please complete the captcha verification");
        return;
      }
    }

    const success = await login({ username, password, remember_me: rememberMe, recaptcha_token: recaptchaToken });
    if (success) {
      router.push("/dashboard");
    }
  };

  const displayError = localError || error;

  return (
    <Card variant="glass">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20">
          <Lock className="h-6 w-6 text-primary" />
        </div>
        <CardTitle className="text-2xl">Welcome Back</CardTitle>
        <CardDescription>Sign in to access your tools</CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {successMessage && (
            <Alert variant="success">{successMessage}</Alert>
          )}

          {displayError && (
            <Alert variant="error">{displayError}</Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="username" required>
              Username
            </Label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="pl-10"
                autoComplete="username"
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" required>
              Password
            </Label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10"
                autoComplete="current-password"
                disabled={isLoading}
              />
            </div>
          </div>

          {recaptchaSiteKey && (
            <div className="flex justify-center">
              <ReCAPTCHA
                ref={recaptchaRef}
                sitekey={recaptchaSiteKey}
                theme={theme}
              />
            </div>
          )}

          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-surface-600 bg-surface-700 text-primary focus:ring-primary"
                disabled={isLoading}
              />
              <span className="text-sm text-text-muted">Keep me signed in</span>
            </label>
            <Link
              href="/forgot-password"
              className="text-sm text-primary hover:text-primary-hover transition-colors"
            >
              Forgot password?
            </Link>
          </div>
        </CardContent>

        <CardFooter className="flex flex-col gap-4">
          <Button
            type="submit"
            variant="glow"
            className="w-full"
            isLoading={isLoading}
          >
            Sign In
          </Button>

          <p className="text-center text-sm text-text-muted">
            Don&apos;t have an account?{" "}
            <Link
              href="/register"
              className="text-primary hover:text-primary-hover transition-colors"
            >
              Sign up
            </Link>
          </p>
        </CardFooter>
      </form>
    </Card>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="flex justify-center p-8">Loading...</div>}>
      <LoginForm />
    </Suspense>
  );
}