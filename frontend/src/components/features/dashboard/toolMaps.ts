/**
 * Shared lookup maps for dashboard tool rendering.
 *
 * Backend tools store a Lucide icon name (Tool.icon) — iconMap resolves the
 * ones we ship (explicit imports keep Lucide tree-shakeable). Tool names from
 * the backend are title-cased ("Tax Calculator"); slugify() normalizes them
 * for route/icon fallbacks.
 */

import {
  Calculator,
  FileText,
  Mail,
  Clock,
  Coins,
  Code,
  PenLine,
  Megaphone,
  BarChart3,
  Wrench,
  type LucideIcon,
} from "lucide-react";

export function slugify(name: string): string {
  return name.trim().toLowerCase().replace(/[\s_]+/g, "-");
}

/** Lucide icon name (from Tool.icon) → component */
const iconByName: Record<string, LucideIcon> = {
  calculator: Calculator,
  "file-text": FileText,
  mail: Mail,
  clock: Clock,
  coins: Coins,
  code: Code,
  "pen-line": PenLine,
  megaphone: Megaphone,
  "bar-chart": BarChart3,
};

/** Tool slug → icon fallback when Tool.icon is not set */
const iconBySlug: Record<string, LucideIcon> = {
  "tax-calculator": Calculator,
  "unified-tax-calculator": Calculator,
  "canada-tax-calculator": Calculator,
  "char-counter": FileText,
  "character-counter": FileText,
  "email-templates": Mail,
  "unix-timestamp": Clock,
  "unix-timestamp-converter": Clock,
};

export function getToolIcon(iconName: string | null, toolName: string): LucideIcon {
  if (iconName && iconByName[iconName]) return iconByName[iconName];
  return iconBySlug[slugify(toolName)] || Wrench;
}

/** Tool slug → Next.js route. Route group "(dashboard)" adds no URL segment. */
const routeBySlug: Record<string, string> = {
  "tax-calculator": "/tools/tax-calculator",
  "unified-tax-calculator": "/tools/tax-calculator",
  "canada-tax-calculator": "/tools/tax-calculator",
  "char-counter": "/tools/char-counter",
  "character-counter": "/tools/char-counter",
  "email-templates": "/tools/email-templates",
  "unix-timestamp": "/tools/unix-timestamp",
  "unix-timestamp-converter": "/tools/unix-timestamp",
};

export function getToolRoute(toolName: string): string {
  const slug = slugify(toolName);
  return routeBySlug[slug] || `/tools/${slug}`;
}
