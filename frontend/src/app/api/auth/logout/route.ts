import { NextResponse } from "next/server";
import { cookies } from "next/headers";

const FLASK_URL = process.env.FLASK_BACKEND_URL || "http://127.0.0.1:5000";

export async function POST() {
  try {
    const cookieStore = await cookies();
    const sessionCookie = cookieStore.get("session");

    if (sessionCookie) {
      // Call Flask's logout endpoint
      await fetch(`${FLASK_URL}/logout`, {
        method: "GET",
        headers: {
          Cookie: `session=${sessionCookie.value}`,
        },
        redirect: "manual",
      });
    }

    // Clear the session cookie
    const response = NextResponse.json({
      status: "success",
      message: "Logged out successfully",
    });

    response.cookies.delete("session");

    return response;
  } catch (error) {
    console.error("Logout error:", error);
    return NextResponse.json({
      status: "success",
      message: "Logged out",
    });
  }
}
