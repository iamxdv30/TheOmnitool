import { NextRequest, NextResponse } from "next/server";

const FLASK_URL = process.env.FLASK_BACKEND_URL || "http://127.0.0.1:5000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { username, password, remember_me, recaptcha_token } = body;

    // Create form data for Flask's form-based login
    const formData = new URLSearchParams();
    formData.append("username", username || "");
    formData.append("password", password || "");
    if (recaptcha_token) {
      formData.append("g-recaptcha-response", recaptcha_token);
    }
    if (remember_me) {
      formData.append("remember_me", "on");
    }

    // Call Flask's login endpoint
    const response = await fetch(`${FLASK_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
      redirect: "manual", // Don't follow redirects, we need to check the response
      credentials: "include",
    });

    // Get cookies from Flask response
    const setCookieHeader = response.headers.get("set-cookie");

    // Check if login was successful (Flask redirects on success)
    if (response.status === 302 || response.status === 301) {
      const location = response.headers.get("location") || "";
      
      // Check if redirected to dashboard (success) or back to login (failure)
      if (location.includes("dashboard") || location.includes("admin")) {
        const apiResponse = NextResponse.json({
          status: "success",
          data: {
            user: {
              username: username,
            },
          },
        });

        // Forward the session cookie from Flask
        if (setCookieHeader) {
          apiResponse.headers.set("Set-Cookie", setCookieHeader);
        }

        return apiResponse;
      } else if (location.includes("verification_pending")) {
        return NextResponse.json(
          {
            status: "error",
            message: "Your email address must be verified before you can log in.",
            error_code: "EMAIL_NOT_VERIFIED",
          },
          { status: 403 }
        );
      }
    }

    // If we got a 200, Flask rendered the login page again (likely with an error)
    if (response.status === 200) {
      // Try to extract error message from the HTML response
      const html = await response.text();
      
      // Check for common error patterns in Flask flash messages
      if (html.includes("Invalid username or password")) {
        return NextResponse.json(
          { status: "error", message: "Invalid username or password" },
          { status: 401 }
        );
      }
      if (html.includes("captcha")) {
        return NextResponse.json(
          { status: "error", message: "Please complete the captcha verification" },
          { status: 400 }
        );
      }
      if (html.includes("email") && html.includes("verified")) {
        return NextResponse.json(
          {
            status: "error",
            message: "Your email address must be verified before you can log in.",
            error_code: "EMAIL_NOT_VERIFIED",
          },
          { status: 403 }
        );
      }

      // Generic error
      return NextResponse.json(
        { status: "error", message: "Login failed. Please check your credentials." },
        { status: 401 }
      );
    }

    return NextResponse.json(
      { status: "error", message: "Login failed" },
      { status: response.status }
    );
  } catch (error) {
    console.error("Login API error:", error);
    return NextResponse.json(
      { status: "error", message: "An error occurred during login" },
      { status: 500 }
    );
  }
}
