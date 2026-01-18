"use client";

import { useState, use } from "react";
import { useRouter } from "next/navigation";
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
  Alert,
  Label,
} from "@/components/ui";
import { PasswordInput, PasswordStrength } from "@/components/forms";
import { useAuth } from "@/hooks";
import { resetPasswordSchema, type ResetPasswordFormData } from "@/lib/validations";
import { Lock, CheckCircle, ArrowLeft } from "lucide-react";

interface ResetPasswordPageProps {
  params: Promise<{ token: string }>;
}

export default function ResetPasswordPage({ params }: ResetPasswordPageProps) {
  const { token } = use(params);
  const router = useRouter();
  const { resetPassword, isLoading, error, clearError } = useAuth();
  const [isSuccess, setIsSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: "",
      confirmPassword: "",
    },
  });

  const password = watch("password");

  const onSubmit = async (data: ResetPasswordFormData) => {
    clearError();
    const success = await resetPassword(token, data.password);
    if (success) {
      setIsSuccess(true);
      // Redirect to login after 3 seconds
      setTimeout(() => {
        router.push("/login");
      }, 3000);
    }
  };

  if (isSuccess) {
    return (
      <Card variant="glass" className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-success/20">
            <CheckCircle className="h-6 w-6 text-success" />
          </div>
          <CardTitle className="text-2xl">Password Reset!</CardTitle>
          <CardDescription>
            Your password has been successfully reset. Redirecting you to sign in...
          </CardDescription>
        </CardHeader>

        <CardFooter className="flex justify-center">
          <Link
            href="/login"
            className="flex items-center gap-2 text-sm text-primary hover:text-primary-hover transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Go to sign in now
          </Link>
        </CardFooter>
      </Card>
    );
  }

  return (
    <Card variant="glass" className="w-full max-w-md">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20">
          <Lock className="h-6 w-6 text-primary" />
        </div>
        <CardTitle className="text-2xl">Reset Password</CardTitle>
        <CardDescription>
          Enter your new password below
        </CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {error && <Alert variant="error">{error}</Alert>}

          {/* New Password */}
          <div className="space-y-2">
            <Label htmlFor="password" required>
              New Password
            </Label>
            <PasswordInput
              id="password"
              placeholder="Create a strong password"
              autoComplete="new-password"
              disabled={isLoading}
              error={errors.password?.message}
              {...register("password")}
            />
            {errors.password && (
              <p className="text-xs text-danger">{errors.password.message}</p>
            )}
            <PasswordStrength password={password || ""} />
          </div>

          {/* Confirm Password */}
          <div className="space-y-2">
            <Label htmlFor="confirmPassword" required>
              Confirm New Password
            </Label>
            <PasswordInput
              id="confirmPassword"
              placeholder="Confirm your new password"
              autoComplete="new-password"
              disabled={isLoading}
              error={errors.confirmPassword?.message}
              {...register("confirmPassword")}
            />
            {errors.confirmPassword && (
              <p className="text-xs text-danger">
                {errors.confirmPassword.message}
              </p>
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
            Reset Password
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
