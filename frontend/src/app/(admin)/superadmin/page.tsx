"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui";
import { Button } from "@/components/ui/Button";
import {
  UserTable,
  CreateUserDialog,
  UpdateUserDialog,
  ToolAccessDialog,
} from "@/components/features/admin";
import { api, isSuccess } from "@/lib/api";
import { toast } from "@/store/uiStore";
import { useAuth } from "@/hooks";
import type { AdminUser } from "@/types";
import { Shield, Users, UserPlus, Loader2, Wrench } from "lucide-react";
import Link from "next/link";

const USERS_PER_PAGE = 10;

interface UsersResponse {
  users: AdminUser[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export default function SuperAdminDashboardPage() {
  const { user } = useAuth();
  const router = useRouter();

  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [totalUsers, setTotalUsers] = useState(0);

  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);
  const [accessUser, setAccessUser] = useState<AdminUser | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (user && user.role !== "superadmin") {
      router.push("/admin");
    }
  }, [user, router]);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    const response = await api.get<UsersResponse>("/admin/users", {
      params: {
        page: currentPage,
        per_page: USERS_PER_PAGE,
        search: searchQuery,
      },
    });

    if (isSuccess(response)) {
      setUsers(response.data.users);
      setTotalPages(response.data.total_pages);
      setTotalUsers(response.data.total);
    } else {
      toast.error(response.message || "Failed to load users");
    }
    setIsLoading(false);
  }, [currentPage, searchQuery]);

  useEffect(() => {
    const loadUsers = async () => {
      await fetchUsers();
    };
    loadUsers();
  }, [fetchUsers]);

  const handleCreateUser = async (data: {
    username: string;
    email: string;
    password: string;
    fname?: string;
    lname?: string;
    role: "user" | "admin";
  }) => {
    setIsProcessing(true);
    const response = await api.post("/admin/users", data);

    if (isSuccess(response)) {
      toast.success("User created successfully");
      setShowCreateDialog(false);
      fetchUsers();
    } else {
      toast.error(response.message || "Failed to create user");
    }
    setIsProcessing(false);
  };

  const handleUpdateUser = async (
    userId: number,
    data: {
      fname?: string;
      lname?: string;
      address?: string;
      city?: string;
      state?: string;
      zip?: string;
      role?: "user" | "admin" | "superadmin";
    }
  ) => {
    setIsProcessing(true);

    if (data.role) {
      const roleResponse = await api.post(`/admin/change-role/${userId}`, {
        role: data.role,
      });

      if (!isSuccess(roleResponse)) {
        toast.error(roleResponse.message || "Failed to change role");
        setIsProcessing(false);
        return;
      }
    }

    const { role: _role, ...profileData } = data;
    const response = await api.put(`/admin/users/${userId}`, profileData);

    if (isSuccess(response)) {
      toast.success("User updated successfully");
      setEditingUser(null);
      fetchUsers();
    } else {
      toast.error(response.message || "Failed to update user");
    }
    setIsProcessing(false);
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm("Are you sure you want to delete this user?")) return;

    const response = await api.delete(`/admin/users/${userId}`);

    if (isSuccess(response)) {
      toast.success("User deleted successfully");
      fetchUsers();
    } else {
      toast.error(response.message || "Failed to delete user");
    }
  };

  const handleGrantAccess = async (userId: number, toolName: string) => {
    const response = await api.post("/admin/grant-tool-access", {
      user_id: userId,
      tool_name: toolName,
    });

    if (isSuccess(response)) {
      toast.success("Tool access granted");
      fetchUsers();
      if (accessUser) {
        setAccessUser({
          ...accessUser,
          tools: [...(accessUser.tools || []), toolName],
        });
      }
    } else {
      toast.error(response.message || "Failed to grant access");
    }
  };

  const handleRevokeAccess = async (userId: number, toolName: string) => {
    const response = await api.post("/admin/revoke-tool-access", {
      user_id: userId,
      tool_name: toolName,
    });

    if (isSuccess(response)) {
      toast.success("Tool access revoked");
      fetchUsers();
      if (accessUser) {
        setAccessUser({
          ...accessUser,
          tools: (accessUser.tools || []).filter((t) => t !== toolName),
        });
      }
    } else {
      toast.error(response.message || "Failed to revoke access");
    }
  };

  if (user?.role !== "superadmin") {
    return null;
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-text-high flex items-center gap-3">
            <Shield className="h-8 w-8 text-danger" />
            SuperAdmin Dashboard
          </h1>
          <p className="mt-2 text-text-muted">
            Full system control including role management.
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <UserPlus className="mr-2 h-4 w-4" />
          Create User
        </Button>
      </div>

      {/* Stats & Quick Actions */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card variant="glass">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/20">
                <Users className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-text-muted">Total Users</p>
                <p className="font-display text-2xl font-bold text-text-high">
                  {isLoading ? <Loader2 className="h-6 w-6 animate-spin" /> : totalUsers}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Link href="/superadmin/tools">
          <Card variant="interactive" className="h-full hover:border-primary/50">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-warning/20">
                  <Wrench className="h-6 w-6 text-warning" />
                </div>
                <div>
                  <p className="text-sm text-text-muted">Manage Tools</p>
                  <p className="font-medium text-text-high">Configure system tools →</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* User Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            User Management
          </CardTitle>
          <CardDescription>
            View, edit, manage users and change roles (SuperAdmin only).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <UserTable
            users={users}
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            onEdit={setEditingUser}
            onDelete={handleDeleteUser}
            onManageAccess={setAccessUser}
            isLoading={isLoading}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            canChangeRole={true}
          />
        </CardContent>
      </Card>

      {/* Dialogs */}
      <CreateUserDialog
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onSubmit={handleCreateUser}
        isLoading={isProcessing}
        canCreateAdmin={true}
      />

      <UpdateUserDialog
        isOpen={!!editingUser}
        user={editingUser}
        onClose={() => setEditingUser(null)}
        onSubmit={handleUpdateUser}
        isLoading={isProcessing}
        canChangeRole={true}
      />

      <ToolAccessDialog
        isOpen={!!accessUser}
        user={accessUser}
        onClose={() => setAccessUser(null)}
        onGrant={handleGrantAccess}
        onRevoke={handleRevokeAccess}
        isLoading={isProcessing}
      />
    </div>
  );
}
