import { NextResponse } from "next/server";

/**
 * Health check endpoint for the Next.js frontend.
 * Used by CI/CD pipelines to verify dual-stack deployment health.
 *
 * GET /api/health
 *
 * Returns:
 * - status: "healthy" if both Next.js and Flask are up
 * - status: "degraded" if Next.js is up but Flask is down
 * - services: Individual service status
 */
export async function GET() {
  const startTime = Date.now();

  // Check Flask backend health
  let flaskStatus: "up" | "down" = "down";
  let flaskResponseTime: number | null = null;

  try {
    const flaskStart = Date.now();
    const flaskResponse = await fetch("http://127.0.0.1:5000/health/ping", {
      method: "GET",
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });

    if (flaskResponse.ok) {
      flaskStatus = "up";
      flaskResponseTime = Date.now() - flaskStart;
    }
  } catch {
    // Flask is not reachable
    flaskStatus = "down";
  }

  const totalResponseTime = Date.now() - startTime;

  // Determine overall status
  const overallStatus = flaskStatus === "up" ? "healthy" : "degraded";

  return NextResponse.json(
    {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      responseTime: totalResponseTime,
      services: {
        nextjs: {
          status: "up",
        },
        flask: {
          status: flaskStatus,
          responseTime: flaskResponseTime,
        },
      },
    },
    {
      status: overallStatus === "healthy" ? 200 : 503,
    }
  );
}
