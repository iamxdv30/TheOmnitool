"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/forms";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui";
import { X, Loader2, UserPlus } from "lucide-react";

const createUserSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters"),
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  fname: z.string().optional(),
  lname: z.string().optional(),
  role: z.enum(["user", "admin"]),
});

type CreateUserFormData = z.infer<typeof createUserSchema>;

interface CreateUserDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateUserFormData) => Promise<void>;
  isLoading?: boolean;
  canCreateAdmin?: boolean;
}

export function CreateUserDialog({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
  canCreateAdmin = false,
}: CreateUserDialogProps) {
  const form = useForm<CreateUserFormData>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
      fname: "",
      lname: "",
      role: "user",
    },
  });

  const handleSubmit = async (data: CreateUserFormData) => {
    await onSubmit(data);
    form.reset();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <Card className="relative z-10 w-full max-w-md">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <UserPlus className="h-5 w-5 text-primary" />
            Create New User
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0">
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField
                name="fname"
                control={form.control}
                label="First Name"
                placeholder="John"
              />
              <FormField
                name="lname"
                control={form.control}
                label="Last Name"
                placeholder="Doe"
              />
            </div>

            <FormField
              name="username"
              control={form.control}
              label="Username"
              placeholder="johndoe"
              required
            />

            <FormField
              name="email"
              control={form.control}
              label="Email"
              type="email"
              placeholder="john@example.com"
              required
            />

            <FormField
              name="password"
              control={form.control}
              label="Password"
              type="password"
              placeholder="Min 8 characters"
              required
            />

            <div className="space-y-2">
              <label className="text-sm font-medium text-text-high">Role</label>
              <select
                {...form.register("role")}
                className="w-full rounded-lg border border-surface-700 bg-surface-800 px-3 py-2 text-text-high focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary-glow"
              >
                <option value="user">User</option>
                {canCreateAdmin && <option value="admin">Admin</option>}
              </select>
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" disabled={isLoading} className="flex-1">
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <UserPlus className="mr-2 h-4 w-4" />
                )}
                Create User
              </Button>
              <Button type="button" variant="ghost" onClick={onClose}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
