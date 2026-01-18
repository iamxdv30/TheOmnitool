"use client";

import { useState } from "react";
import type { AdminUser } from "@/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import {
  Edit,
  Trash2,
  Key,
  Search,
  ChevronLeft,
  ChevronRight,
  MoreVertical,
} from "lucide-react";

interface UserTableProps {
  users: AdminUser[];
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onEdit: (user: AdminUser) => void;
  onDelete: (userId: number) => void;
  onManageAccess: (user: AdminUser) => void;
  isLoading?: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  canChangeRole?: boolean;
}

export function UserTable({
  users,
  currentPage,
  totalPages,
  onPageChange,
  onEdit,
  onDelete,
  onManageAccess,
  isLoading,
  searchQuery,
  onSearchChange,
  canChangeRole = false,
}: UserTableProps) {
  const [menuOpenId, setMenuOpenId] = useState<number | null>(null);

  const getRoleBadgeClass = (role: string) => {
    switch (role) {
      case "superadmin":
        return "bg-danger/20 text-danger";
      case "admin":
        return "bg-warning/20 text-warning";
      default:
        return "bg-primary/20 text-primary";
    }
  };

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
        <Input
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search users by name, email, or username..."
          className="pl-10"
        />
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-lg border border-surface-700">
        <table className="w-full">
          <thead className="bg-surface-800">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-text-muted">
                User
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-text-muted">
                Email
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-text-muted">
                Role
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-text-muted">
                Tools
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-text-muted">
                Status
              </th>
              <th className="px-4 py-3 text-right text-sm font-medium text-text-muted">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-700">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-text-muted">
                  Loading users...
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-text-muted">
                  No users found
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.id} className="hover:bg-surface-800/50">
                  <td className="px-4 py-3">
                    <div>
                      <p className="font-medium text-text-high">
                        {user.fname && user.lname
                          ? `${user.fname} ${user.lname}`
                          : user.username}
                      </p>
                      <p className="text-sm text-text-muted">@{user.username}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-text-high">{user.email}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-xs font-medium capitalize ${getRoleBadgeClass(
                        user.role
                      )}`}
                    >
                      {user.role}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-text-muted">
                    {user.tools?.length || 0} tools
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                        user.email_verified
                          ? "bg-success/20 text-success"
                          : "bg-warning/20 text-warning"
                      }`}
                    >
                      {user.email_verified ? "Verified" : "Pending"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="relative flex justify-end">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          setMenuOpenId(menuOpenId === user.id ? null : user.id)
                        }
                        className="h-8 w-8 p-0"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                      {menuOpenId === user.id && (
                        <>
                          <div
                            className="fixed inset-0 z-10"
                            onClick={() => setMenuOpenId(null)}
                          />
                          <div className="absolute right-0 top-8 z-20 w-40 rounded-lg border border-surface-700 bg-surface-800 py-1 shadow-lg">
                            <button
                              onClick={() => {
                                onEdit(user);
                                setMenuOpenId(null);
                              }}
                              className="flex w-full items-center gap-2 px-3 py-2 text-sm text-text-high hover:bg-surface-700"
                            >
                              <Edit className="h-4 w-4" />
                              Edit User
                            </button>
                            <button
                              onClick={() => {
                                onManageAccess(user);
                                setMenuOpenId(null);
                              }}
                              className="flex w-full items-center gap-2 px-3 py-2 text-sm text-text-high hover:bg-surface-700"
                            >
                              <Key className="h-4 w-4" />
                              Tool Access
                            </button>
                            {(canChangeRole || user.role === "user") && (
                              <button
                                onClick={() => {
                                  onDelete(user.id);
                                  setMenuOpenId(null);
                                }}
                                className="flex w-full items-center gap-2 px-3 py-2 text-sm text-danger hover:bg-surface-700"
                              >
                                <Trash2 className="h-4 w-4" />
                                Delete User
                              </button>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-text-muted">
            Page {currentPage} of {totalPages}
          </p>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
