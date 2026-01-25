/**
 * Next.js Middleware for Route Protection
 * Based on Phase 3 spec (Section 4.3)
 * 
 * - Redirects unauthenticated users to login
 * - Protects admin routes
 * - Allows public routes without auth
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Routes that don't require authentication
 */
const PUBLIC_ROUTES = [
  "/login",
  "/register",
  "/forgot-password",
  "/reset-password",
  "/verification-pending",
  "/",
  "/about",
  "/contact",
];

/**
 * Routes that require admin role (checked client-side after /auth/status)
 */
const ADMIN_ROUTES = ["/admin"];

/**
 * Check if path matches any route pattern
 */
function matchesRoute(path: string, routes: string[]): boolean {
  return routes.some((route) => {
    if (route === path) return true;
    if (path.startsWith(`${route}/`)) return true;
    return false;
  });
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip middleware for static files and API routes
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".") // Static files like favicon.ico
  ) {
    return NextResponse.next();
  }

  // Check for session cookie
  const sessionCookie = request.cookies.get("session");

  // Allow public routes without authentication
  if (matchesRoute(pathname, PUBLIC_ROUTES)) {
    // If user is authenticated and tries to access login/register, redirect to dashboard
    if (sessionCookie && (pathname === "/login" || pathname === "/register")) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
    return NextResponse.next();
  }

  // Redirect to login if no session cookie
  if (!sessionCookie) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Admin routes: cookie exists but role check happens client-side
  // We can't decode the session cookie here (it's encrypted by Flask)
  // The client will check /auth/status and redirect if not admin

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!_next/static|_next/image|favicon.ico|public/).*)",
  ],
};
