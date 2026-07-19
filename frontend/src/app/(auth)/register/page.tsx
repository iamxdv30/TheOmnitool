"use client";

import { useState } from "react";
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
  Input,
  Label,
  Alert,
} from "@/components/ui";
import { PasswordInput, PasswordStrength } from "@/components/forms";
import { useAuth } from "@/hooks";
import { registerSchema, type RegisterFormData } from "@/lib/validations";
import { UserPlus, User, Mail, AtSign } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const { register: registerUser, isLoading, error, clearError } = useAuth();
  const [registeredEmail, setRegisteredEmail] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const password = watch("password");

  const onSubmit = async (data: RegisterFormData) => {
    clearError();

    const result = await registerUser(data);
    if (result.success) {
      setRegisteredEmail(data.email);
      if (result.requiresVerification) {
        router.push(`/verification-pending?email=${encodeURIComponent(data.email)}`);
      } else {
        router.push("/dashboard");
      }
    }
  };

  return (
    <Card variant="glass" className="w-full max-w-md">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/20">
          <UserPlus className="h-6 w-6 text-primary" />
        </div>
        <CardTitle className="text-2xl">Create Account</CardTitle>
        <CardDescription>Join The Omnitool today</CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {error && <Alert variant="error">{error}</Alert>}

          {/* Full Name */}
          <div className="space-y-2">
            <Label htmlFor="name" required>
              Full Name
            </Label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                className="pl-10"
                autoComplete="name"
                disabled={isLoading}
                error={errors.name?.message}
                {...register("name")}
              />
            </div>
            {errors.name && (
              <p className="text-xs text-danger">{errors.name.message}</p>
            )}
          </div>

          {/* Username */}
          <div className="space-y-2">
            <Label htmlFor="username" required>
              Username
            </Label>
            <div className="relative">
              <AtSign className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
              <Input
                id="username"
                type="text"
                placeholder="johndoe"
                className="pl-10"
                autoComplete="username"
                disabled={isLoading}
                error={errors.username?.message}
                {...register("username")}
              />
            </div>
            {errors.username ? (
              <p className="text-xs text-danger">{errors.username.message}</p>
            ) : (
              <p className="text-xs text-text-muted">
                3-50 characters, letters, numbers, and underscores only
              </p>
            )}
          </div>

          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="email" required>
              Email
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

          {/* Password */}
          <div className="space-y-2">
            <Label htmlFor="password" required>
              Password
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
              Confirm Password
            </Label>
            <PasswordInput
              id="confirmPassword"
              placeholder="Confirm your password"
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
            Create Account
          </Button>

          <p className="text-center text-sm text-text-muted">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-primary hover:text-primary-hover transition-colors"
            >
              Sign in
            </Link>
          </p>
        </CardFooter>
      </form>
    </Card>
  );
}
