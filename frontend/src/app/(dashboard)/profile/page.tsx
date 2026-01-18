"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useAuth, useProfile } from "@/hooks";
import {
  profileSchema,
  passwordChangeSchema,
  type ProfileFormData,
  type PasswordChangeFormData,
} from "@/lib/validations";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui";
import { Button } from "@/components/ui/Button";
import { FormField } from "@/components/forms";
import { PasswordStrength } from "@/components/forms/PasswordStrength";
import { toast } from "@/components/feedback/Toaster";
import { Loader2, User, Lock, Save } from "lucide-react";

export default function ProfilePage() {
  const { user, checkAuth } = useAuth();
  const { getProfile, updateProfile, changePassword, isLoading } = useProfile();
  const [isProfileLoading, setIsProfileLoading] = useState(true);

  const profileForm = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      fname: "",
      lname: "",
      address: "",
      city: "",
      state: "",
      zip: "",
    },
  });

  const passwordForm = useForm<PasswordChangeFormData>({
    resolver: zodResolver(passwordChangeSchema),
    defaultValues: {
      currentPassword: "",
      newPassword: "",
      confirmNewPassword: "",
    },
  });

  const newPassword = passwordForm.watch("newPassword");

  useEffect(() => {
    async function loadProfile() {
      setIsProfileLoading(true);
      const profile = await getProfile();
      if (profile) {
        profileForm.reset({
          fname: profile.fname || "",
          lname: profile.lname || "",
          address: profile.address || "",
          city: profile.city || "",
          state: profile.state || "",
          zip: profile.zip || "",
        });
      }
      setIsProfileLoading(false);
    }
    loadProfile();
  }, [getProfile, profileForm]);

  const onProfileSubmit = async (data: ProfileFormData) => {
    const success = await updateProfile(data);
    if (success) {
      toast.success("Profile updated successfully");
      await checkAuth();
    } else {
      toast.error("Failed to update profile");
    }
  };

  const onPasswordSubmit = async (data: PasswordChangeFormData) => {
    const success = await changePassword({
      currentPassword: data.currentPassword,
      newPassword: data.newPassword,
      confirmNewPassword: data.confirmNewPassword,
    });
    if (success) {
      toast.success("Password changed successfully");
      passwordForm.reset();
    } else {
      toast.error("Failed to change password");
    }
  };

  if (isProfileLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="font-display text-3xl font-bold text-text-high">
          Profile Settings
        </h1>
        <p className="mt-2 text-text-muted">
          Manage your personal information and account security.
        </p>
      </div>

      {/* Account Overview */}
      <Card variant="glass">
        <CardContent className="flex items-center gap-4 p-6">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/20">
            <User className="h-8 w-8 text-primary" />
          </div>
          <div>
            <p className="font-display text-xl font-semibold text-text-high">
              {user?.username}
            </p>
            <p className="text-text-muted">{user?.email}</p>
            <p className="mt-1 text-sm capitalize text-primary">{user?.role}</p>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Personal Information Form */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-primary" />
              <CardTitle>Personal Information</CardTitle>
            </div>
            <CardDescription>
              Update your personal details and address.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={profileForm.handleSubmit(onProfileSubmit)}
              className="space-y-4"
            >
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  name="fname"
                  control={profileForm.control}
                  label="First Name"
                  placeholder="John"
                  autoComplete="given-name"
                />
                <FormField
                  name="lname"
                  control={profileForm.control}
                  label="Last Name"
                  placeholder="Doe"
                  autoComplete="family-name"
                />
              </div>

              <FormField
                name="address"
                control={profileForm.control}
                label="Address"
                placeholder="123 Main Street"
                autoComplete="street-address"
              />

              <div className="grid gap-4 sm:grid-cols-3">
                <FormField
                  name="city"
                  control={profileForm.control}
                  label="City"
                  placeholder="New York"
                  autoComplete="address-level2"
                />
                <FormField
                  name="state"
                  control={profileForm.control}
                  label="State/Region"
                  placeholder="NY"
                  autoComplete="address-level1"
                />
                <FormField
                  name="zip"
                  control={profileForm.control}
                  label="Postal Code"
                  placeholder="10001"
                  autoComplete="postal-code"
                />
              </div>

              <Button
                type="submit"
                disabled={isLoading || !profileForm.formState.isDirty}
                className="w-full sm:w-auto"
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                Save Changes
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Change Password Form */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary" />
              <CardTitle>Change Password</CardTitle>
            </div>
            <CardDescription>
              Update your password to keep your account secure.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={passwordForm.handleSubmit(onPasswordSubmit)}
              className="space-y-4"
            >
              <FormField
                name="currentPassword"
                control={passwordForm.control}
                label="Current Password"
                type="password"
                placeholder="Enter current password"
                autoComplete="current-password"
                required
              />

              <div className="space-y-2">
                <FormField
                  name="newPassword"
                  control={passwordForm.control}
                  label="New Password"
                  type="password"
                  placeholder="Enter new password"
                  autoComplete="new-password"
                  required
                />
                {newPassword && <PasswordStrength password={newPassword} />}
              </div>

              <FormField
                name="confirmNewPassword"
                control={passwordForm.control}
                label="Confirm New Password"
                type="password"
                placeholder="Confirm new password"
                autoComplete="new-password"
                required
              />

              <Button
                type="submit"
                disabled={isLoading || !passwordForm.formState.isDirty}
                className="w-full sm:w-auto"
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Lock className="mr-2 h-4 w-4" />
                )}
                Change Password
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
