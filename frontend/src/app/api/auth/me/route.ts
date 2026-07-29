import { NextResponse } from "next/server";
import { cookies } from "next/headers";

const FLASK_URL = process.env.FLASK_BACKEND_URL || "http://127.0.0.1:5000";

export async function GET() {
  try {
    // Get the session cookie from the request
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get("session");

    if (!sessionCookie) {
      return NextResponse.json(
        { status: "error", message: "Not authenticated" },
        { status: 401 }
      );
    }

    // Call Flask's user dashboard to check if session is valid
    // We use a lightweight endpoint to verify the session
    const response = await fetch(`${FLASK_URL}/dashboard`, {
      method: "GET",
      headers: {
        Cookie: `session=${sessionCookie.value}`,
      },
      redirect: "manual",
    });

    // If Flask redirects to login, session is invalid
    if (response.status === 302 || response.status === 301) {
      const location = response.headers.get("location") || "";
      if (location.includes("login")) {
        return NextResponse.json(
          { status: "error", message: "Not authenticated" },
          { status: 401 }
        );
      }
    }

    // If we get a 200, the session is valid
    if (response.status === 200) {
      // Try to extract user info from the page or return basic info
      // For now, return minimal user data
      return NextResponse.json({
        status: "success",
        data: {
          user: {
            // We don't have full user data without Flask API support
            // Return what we can infer
            authenticated: true,
          },
        },
      });
    }

    return NextResponse.json(
      { status: "error", message: "Not authenticated" },
      { status: 401 }
    );
  } catch (error) {
    console.error("Auth check error:", error);
    return NextResponse.json(
      { status: "error", message: "Authentication check failed" },
      { status: 500 }
    );
  }
}
