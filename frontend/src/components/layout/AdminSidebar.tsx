"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks";
import {
  LayoutDashboard,
  Users,
  Wrench,
  Shield,
  LogOut,
  ArrowLeft,
  type LucideIcon,
} from "lucide-react";
import { Button } from "@/components/ui/Button";

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  superAdminOnly?: boolean;
}

const navItems: NavItem[] = [
  { label: "Admin Dashboard", href: "/admin", icon: LayoutDashboard },
  { label: "User Management", href: "/admin/users", icon: Users },
];

const superAdminItems: NavItem[] = [
  { label: "SuperAdmin Panel", href: "/superadmin", icon: Shield, superAdminOnly: true },
  { label: "Manage Tools", href: "/superadmin/tools", icon: Wrench, superAdminOnly: true },
];

interface AdminSidebarProps {
  isSuperAdmin?: boolean;
}

export function AdminSidebar({ isSuperAdmin = false }: AdminSidebarProps) {
  const pathname = usePathname();
  const { logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    window.location.href = "/login";
  };

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-surface-700 bg-surface-900/95 backdrop-blur-sm">
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-surface-700 px-6">
        <Link href="/admin" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-danger">
            <Shield className="h-4 w-4 text-white" />
          </div>
          <span className="font-display text-xl font-semibold text-text-high">
            Admin Panel
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 p-4">
        {/* Back to Dashboard */}
        <Link
          href="/dashboard"
          className="mb-4 flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-text-muted hover:bg-surface-800 hover:text-text-high transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Link>

        <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-text-muted">
          Administration
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-danger/20 text-danger"
                  : "text-text-muted hover:bg-surface-800 hover:text-text-high"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}

        {isSuperAdmin && (
          <>
            <p className="mb-2 mt-6 px-3 text-xs font-semibold uppercase tracking-wider text-text-muted">
              SuperAdmin
            </p>
            {superAdminItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-danger/20 text-danger"
                      : "text-text-muted hover:bg-surface-800 hover:text-text-high"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.label}
                </Link>
              );
            })}
          </>
        )}

        {/* Logout */}
        <div className="mt-auto pt-6">
          <Button
            variant="ghost"
            onClick={handleLogout}
            className="w-full justify-start text-text-muted hover:text-danger hover:bg-danger/10"
          >
            <LogOut className="mr-2 h-5 w-5" />
            Logout
          </Button>
        </div>
      </nav>
    </aside>
  );
}
