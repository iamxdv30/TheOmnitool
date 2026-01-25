"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Calculator,
  FileText,
  Mail,
  Settings,
  Users,
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

interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  adminOnly?: boolean;
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Tax Calculator", href: "/tools/tax-calculator", icon: Calculator },
  { label: "Character Counter", href: "/tools/char-counter", icon: FileText },
  { label: "Email Templates", href: "/tools/email-templates", icon: Mail },
];

const adminItems: NavItem[] = [
  { label: "User Management", href: "/admin/users", icon: Users, adminOnly: true },
  { label: "Access Control", href: "/admin/access", icon: Shield, adminOnly: true },
];

interface SidebarProps {
  isAdmin?: boolean;
}

export function Sidebar({ isAdmin = false }: SidebarProps) {
  const pathname = usePathname();
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
            className="p-2 text-text-muted hover:text-text-high transition-colors"
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
          "fixed left-0 top-0 z-40 h-screen border-r border-surface-700 bg-surface-900/95 backdrop-blur-sm transition-all duration-300",
          isSidebarCollapsed ? "w-20" : "w-64",
          "md:translate-x-0",
          isMobileOpen ? "translate-x-0 w-64" : "-translate-x-full"
        )}
      >
      {/* Logo */}
      <div className={cn("flex h-16 items-center border-b border-surface-700", isSidebarCollapsed ? "justify-center px-0" : "px-6")}>
        <Link href="/dashboard" className="flex items-center gap-2" title="Omnitool Dashboard">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary shrink-0">
            <span className="font-display text-lg font-bold text-surface-900">O</span>
          </div>
          {!isSidebarCollapsed && (
            <span className="font-display text-xl font-semibold text-text-high truncate">
              Omnitool
            </span>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 p-3">
        {!isSidebarCollapsed && (
          <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-text-muted truncate">
            Tools
          </p>
        )}
        {navItems.map((item) => {
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

        {isAdmin && (
          <>
            {!isSidebarCollapsed && (
              <p className="mb-2 mt-6 px-3 text-xs font-semibold uppercase tracking-wider text-text-muted truncate">
                Admin
              </p>
            )}
             {/* Separator for collapsed mode */}
             {isSidebarCollapsed && <div className="my-2 border-t border-surface-700" />}
             
            {adminItems.map((item) => {
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
        <div className="mt-auto pt-6 flex flex-col gap-1">
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
          <Link
            href="/settings"
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              pathname === "/settings"
                ? "bg-primary/20 text-primary"
                : "text-text-muted hover:bg-surface-800 hover:text-text-high",
               isSidebarCollapsed && "justify-center px-2"
            )}
             title={isSidebarCollapsed ? "Settings" : undefined}
          >
            <Settings className="h-5 w-5 shrink-0" />
            {!isSidebarCollapsed && <span className="truncate">Settings</span>}
          </Link>

          {/* Collapse Toggle Button (Desktop Only) */}
          <button
            onClick={toggleSidebarCollapsed}
            className="hidden md:flex mt-2 items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-text-muted hover:bg-surface-800 hover:text-text-high transition-colors w-full justify-center"
            aria-label={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
             {isSidebarCollapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
          </button>
        </div>
      </nav>
      </aside>
    </>
  );
}
