"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
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
import { forgotPasswordSchema, type ForgotPasswordFormData } from "@/lib/validations";
import { Mail, ArrowLeft, CheckCircle } from "lucide-react";

export default function ForgotPasswordPage() {
  const { forgotPassword, isLoading, error, clearError } = useAuth();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submittedEmail, setSubmittedEmail] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    clearError();
    const success = await forgotPassword(data.email);
    if (success) {
      setSubmittedEmail(data.email);
      setIsSubmitted(true);
    }
  };

  if (isSubmitted) {
    return (
      <Card variant="glass" className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-success/20">
            <CheckCircle className="h-6 w-6 text-success" />
          </div>
          <CardTitle className="text-2xl">Check Your Email</CardTitle>
          <CardDescription>
            We&apos;ve sent password reset instructions to{" "}
            <span className="font-medium text-text-high">{submittedEmail}</span>
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <Alert variant="info">
            If you don&apos;t see the email, check your spam folder. The link
            will expire in 1 hour.
          </Alert>
        </CardContent>

        <CardFooter className="flex flex-col gap-4">
          <Button
            variant="outline"
            className="w-full"
            onClick={() => setIsSubmitted(false)}
          >
            Try another email
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

  return (
    <Card variant="glass" className="w-full max-w-md">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20">
          <Mail className="h-6 w-6 text-primary" />
        </div>
        <CardTitle className="text-2xl">Forgot Password?</CardTitle>
        <CardDescription>
          Enter your email and we&apos;ll send you reset instructions
        </CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {error && <Alert variant="error">{error}</Alert>}

          <div className="space-y-2">
            <Label htmlFor="email" required>
              Email Address
            </Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                className="pl-10"
                autoComplete="email"
                disabled={isLoading}
                error={errors.email?.message}
                {...register("email")}
              />
            </div>
            {errors.email && (
              <p className="text-xs text-danger">{errors.email.message}</p>
            )}
          </div>
        </CardContent>

        <CardFooter className="flex flex-col gap-4">
          <Button
            type="submit"
            variant="glow"
            className="w-full"
            isLoading={isLoading}
          >
            Send Reset Link
          </Button>

          <Link
            href="/login"
            className="flex items-center justify-center gap-2 text-sm text-primary hover:text-primary-hover transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to sign in
          </Link>
        </CardFooter>
      </form>
    </Card>
  );
}
