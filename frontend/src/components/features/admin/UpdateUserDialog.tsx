"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/forms";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui";
import { X, Loader2, Save } from "lucide-react";
import type { AdminUser } from "@/types";

const updateUserSchema = z.object({
  fname: z.string().optional(),
  lname: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  zip: z.string().optional(),
  role: z.enum(["user", "admin", "superadmin"]).optional(),
});

type UpdateUserFormData = z.infer<typeof updateUserSchema>;

interface UpdateUserDialogProps {
  isOpen: boolean;
  user: AdminUser | null;
  onClose: () => void;
  onSubmit: (userId: number, data: UpdateUserFormData) => Promise<void>;
  isLoading?: boolean;
  canChangeRole?: boolean;
}

export function UpdateUserDialog({
  isOpen,
  user,
  onClose,
  onSubmit,
  isLoading = false,
  canChangeRole = false,
}: UpdateUserDialogProps) {
  const form = useForm<UpdateUserFormData>({
    resolver: zodResolver(updateUserSchema),
    defaultValues: {
      fname: "",
      lname: "",
      address: "",
      city: "",
      state: "",
      zip: "",
      role: "user",
    },
  });

  useEffect(() => {
    if (user) {
      form.reset({
        fname: user.fname || "",
        lname: user.lname || "",
        address: user.address || "",
        city: user.city || "",
        state: user.state || "",
        zip: user.zip || "",
        role: user.role,
      });
    }
  }, [user, form]);

  const handleSubmit = async (data: UpdateUserFormData) => {
    if (user) {
      await onSubmit(user.id, data);
    }
  };

  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <Card className="relative z-10 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            Edit User: {user.username}
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
              name="address"
              control={form.control}
              label="Address"
              placeholder="123 Main St"
            />

            <div className="grid gap-4 sm:grid-cols-3">
              <FormField
                name="city"
                control={form.control}
                label="City"
                placeholder="New York"
              />
              <FormField
                name="state"
                control={form.control}
                label="State"
                placeholder="NY"
              />
              <FormField
                name="zip"
                control={form.control}
                label="Zip"
                placeholder="10001"
              />
            </div>

            {canChangeRole && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-text-high">Role</label>
                <select
                  {...form.register("role")}
                  className="w-full rounded-lg border border-surface-700 bg-surface-800 px-3 py-2 text-text-high focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary-glow"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                  <option value="superadmin">SuperAdmin</option>
                </select>
              </div>
            )}

            <div className="flex gap-2 pt-4">
              <Button type="submit" disabled={isLoading} className="flex-1">
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                Save Changes
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
