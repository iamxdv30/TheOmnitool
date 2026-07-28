"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  ArrowLeft,
  LayoutDashboard,
  LogOut,
  Wrench,
  Shield,
  User,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  type LucideIcon,
} from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { useUIStore } from "@/store/uiStore";
import { useAuth } from "@/hooks";

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  adminOnly?: boolean;
}

const navItems: NavItem[] = [
  { label: "All tools", href: "/tools", icon: Wrench },
];

const adminItems: NavItem[] = [
  { label: "Admin Dashboard", href: "/admin", icon: Shield, adminOnly: true },
];

const superAdminItems: NavItem[] = [
  { label: "SuperAdmin Panel", href: "/superadmin", icon: Shield },
  { label: "Manage Tools", href: "/superadmin/tools", icon: Wrench },
];

interface SidebarProps {
  isAdmin?: boolean;
  isSuperAdmin?: boolean;
}

export function Sidebar({ isAdmin = false, isSuperAdmin = false }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuth();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { isSidebarCollapsed, toggleSidebarCollapsed } = useUIStore();

  const closeMobileSidebar = () => setIsMobileOpen(false);

  return (
    <>
      {/* Mobile Header Bar */}
      <div className="fixed left-0 right-0 top-0 z-50 flex h-16 items-center justify-between border-b border-surface-700 bg-surface-900/95 px-4 backdrop-blur-sm md:hidden">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <span className="font-display text-lg font-bold text-surface-900">O</span>
          </div>
          <span className="font-display text-xl font-semibold text-text-high">
            Omnitool
          </span>
        </Link>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <button
            onClick={() => setIsMobileOpen(!isMobileOpen)}
            className="flex h-11 w-11 items-center justify-center text-text-muted transition-colors hover:text-text-high"
            aria-label={isMobileOpen ? "Close menu" : "Open menu"}
          >
            {isMobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={closeMobileSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-40 flex h-screen flex-col border-r border-surface-700 bg-surface-900/95 backdrop-blur-sm transition-all duration-300",
          isSidebarCollapsed ? "w-20" : "w-64",
          "md:translate-x-0",
          isMobileOpen ? "translate-x-0 w-64 top-0 h-screen z-50" : "-translate-x-full"
        )}
      >
      {/* Collapse Toggle Button (Desktop Only) - Inline on Divider */}
      <button
        onClick={toggleSidebarCollapsed}
        className="absolute -right-3 top-6 hidden md:flex h-6 w-6 items-center justify-center rounded-full border border-surface-700 bg-surface-800 text-text-muted hover:bg-surface-700 hover:text-text-high transition-colors shadow-sm z-50"
        aria-label={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
          {isSidebarCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
      </button>

      {/* Logo Area */}
      <div
        className={cn(
          "flex h-16 items-center border-b border-surface-700",
          isSidebarCollapsed ? "justify-center px-0" : "px-6"
        )}
      >
        <Link
          href="/dashboard"
          className="flex items-center gap-2"
          title={isSidebarCollapsed ? "Omnitool Dashboard" : undefined}
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary">
            <span className="font-display text-lg font-bold text-surface-900">O</span>
          </div>
          {!isSidebarCollapsed && (
            <span className="truncate font-display text-xl font-semibold text-text-high">
              Omnitool
            </span>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-3 pt-6">
        {/* Dashboard Link (Always at top) */}
        <Link
          href="/dashboard"
          className={cn(
            "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors mb-2",
            pathname === "/dashboard"
              ? "bg-primary/20 text-primary"
              : "text-text-muted hover:bg-surface-800 hover:text-text-high",
            isSidebarCollapsed && "justify-center px-2"
          )}
          title={isSidebarCollapsed ? "Dashboard" : undefined}
          aria-current={pathname === "/dashboard" ? "page" : undefined}
        >
          <LayoutDashboard className="h-5 w-5 shrink-0" />
          {!isSidebarCollapsed && <span className="truncate">Dashboard</span>}
        </Link>

        {/* Separator for collapsed mode */}
        {isSidebarCollapsed && <div className="my-2 border-t border-surface-700" />}

        <button
          type="button"
          onClick={() => router.back()}
          className={cn(
            "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-text-muted transition-colors hover:bg-surface-800 hover:text-text-high focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-glow focus-visible:ring-offset-2 focus-visible:ring-offset-surface-900",
            isSidebarCollapsed && "justify-center px-2"
          )}
          aria-label="Back"
          title={isSidebarCollapsed ? "Back" : undefined}
        >
          <ArrowLeft className="h-5 w-5 shrink-0" />
          {!isSidebarCollapsed && <span className="truncate">Back</span>}
        </button>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href || pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/20 text-primary"
                  : "text-text-muted hover:bg-surface-800 hover:text-text-high",
                isSidebarCollapsed && "justify-center px-2"
              )}
              title={isSidebarCollapsed ? item.label : undefined}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!isSidebarCollapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}

        {isAdmin && (
          <>
            {!isSidebarCollapsed && (
              <p className="mb-2 mt-6 px-3 text-xs font-semibold uppercase tracking-wider text-text-muted truncate">
                Admin
              </p>
            )}
             {/* Separator for collapsed mode */}
             {isSidebarCollapsed && <div className="my-2 border-t border-surface-700" />}
             
            {[...adminItems, ...(isSuperAdmin ? superAdminItems : [])].map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary/20 text-primary"
                      : "text-text-muted hover:bg-surface-800 hover:text-text-high",
                    isSidebarCollapsed && "justify-center px-2"
                  )}
                   title={isSidebarCollapsed ? item.label : undefined}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  {!isSidebarCollapsed && <span className="truncate">{item.label}</span>}
                </Link>
              );
            })}
          </>
        )}

        {/* Account section at bottom */}
        <div className="mt-auto pt-6 flex flex-col gap-1 pb-6">
           {!isSidebarCollapsed && (
            <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-text-muted truncate">
              Account
            </p>
          )}
           {isSidebarCollapsed && <div className="my-2 border-t border-surface-700" />}

          <Link
            href="/profile"
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              pathname === "/profile"
                ? "bg-primary/20 text-primary"
                : "text-text-muted hover:bg-surface-800 hover:text-text-high",
               isSidebarCollapsed && "justify-center px-2"
            )}
             title={isSidebarCollapsed ? "Profile" : undefined}
          >
            <User className="h-5 w-5 shrink-0" />
            {!isSidebarCollapsed && <span className="truncate">Profile</span>}
          </Link>
          <button
            type="button"
            onClick={() => void logout()}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-text-muted transition-colors hover:bg-surface-800 hover:text-text-high focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-glow focus-visible:ring-offset-2 focus-visible:ring-offset-surface-900",
              isSidebarCollapsed && "justify-center px-2"
            )}
            aria-label="Log out"
            title={isSidebarCollapsed ? "Log out" : undefined}
          >
            <LogOut className="h-5 w-5 shrink-0" />
            {!isSidebarCollapsed && <span className="truncate">Log out</span>}
          </button>
          <div
            className={cn(
              "flex items-center rounded-lg px-3 py-2 text-sm font-medium text-text-muted",
              isSidebarCollapsed ? "justify-center px-2" : "justify-between"
            )}
          >
            {!isSidebarCollapsed && <span>Theme</span>}
            <ThemeToggle />
          </div>
        </div>
      </nav>
      </aside>
    </>
  );
}
