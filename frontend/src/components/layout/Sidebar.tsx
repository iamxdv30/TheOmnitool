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
  type LucideIcon,
} from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";

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
  const [isOpen, setIsOpen] = useState(false);

  const closeSidebar = () => setIsOpen(false);

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
            onClick={() => setIsOpen(!isOpen)}
            className="p-2 text-text-muted hover:text-text-high transition-colors"
            aria-label={isOpen ? "Close menu" : "Open menu"}
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen w-64 border-r border-surface-700 bg-surface-900/95 backdrop-blur-sm transition-transform duration-300",
          "md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-surface-700 px-6">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <span className="font-display text-lg font-bold text-surface-900">O</span>
          </div>
          <span className="font-display text-xl font-semibold text-text-high">
            Omnitool
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 p-4">
        <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-text-muted">
          Tools
        </p>
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
                  : "text-text-muted hover:bg-surface-800 hover:text-text-high"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}

        {isAdmin && (
          <>
            <p className="mb-2 mt-6 px-3 text-xs font-semibold uppercase tracking-wider text-text-muted">
              Admin
            </p>
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

        {/* Account section at bottom */}
        <div className="mt-auto pt-6">
          <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-text-muted">
            Account
          </p>
          <Link
            href="/profile"
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              pathname === "/profile"
                ? "bg-primary/20 text-primary"
                : "text-text-muted hover:bg-surface-800 hover:text-text-high"
            )}
          >
            <User className="h-5 w-5" />
            Profile
          </Link>
          <Link
            href="/settings"
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              pathname === "/settings"
                ? "bg-primary/20 text-primary"
                : "text-text-muted hover:bg-surface-800 hover:text-text-high"
            )}
          >
            <Settings className="h-5 w-5" />
            Settings
          </Link>
        </div>
      </nav>
      </aside>
    </>
  );
}
