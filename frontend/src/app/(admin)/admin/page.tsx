"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui";
import { Button } from "@/components/ui/Button";
import {
  UserTable,
  CreateUserDialog,
  UpdateUserDialog,
  ToolAccessDialog,
} from "@/components/features/admin";
import { api, isSuccess } from "@/lib/api";
import { toast } from "@/components/feedback/Toaster";
import type { AdminUser } from "@/types";
import { Users, UserPlus, Loader2 } from "lucide-react";

const USERS_PER_PAGE = 10;

interface UsersResponse {
  users: AdminUser[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export default function AdminDashboardPage() {
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
    const response = await api.put(`/admin/users/${userId}`, data);

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

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-text-high">
            Admin Dashboard
          </h1>
          <p className="mt-2 text-text-muted">
            Manage users, permissions, and system settings.
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <UserPlus className="mr-2 h-4 w-4" />
          Create User
        </Button>
      </div>

      {/* Stats */}
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
      </div>

      {/* User Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            User Management
          </CardTitle>
          <CardDescription>
            View, edit, and manage user accounts and permissions.
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
          />
        </CardContent>
      </Card>

      {/* Dialogs */}
      <CreateUserDialog
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onSubmit={handleCreateUser}
        isLoading={isProcessing}
      />

      <UpdateUserDialog
        isOpen={!!editingUser}
        user={editingUser}
        onClose={() => setEditingUser(null)}
        onSubmit={handleUpdateUser}
        isLoading={isProcessing}
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
