#!/bin/bash
# =============================================================================
# Production Startup Script for Dual-Stack Deployment (Flask + Next.js)
# =============================================================================
# This script starts both Flask (Gunicorn) and Next.js on a single Heroku dyno.
# Flask runs in the background on port 5000, Next.js runs in foreground on $PORT.
# =============================================================================

set -e

echo "=========================================="
echo "Starting Dual-Stack Server (Flask + Next.js)"
echo "=========================================="

# Configuration
FLASK_PORT=5000
FLASK_WORKERS=2
FLASK_TIMEOUT=120
STARTUP_TIMEOUT=60

# Start Flask (Gunicorn) in background
echo "Starting Flask on port $FLASK_PORT..."
gunicorn -b 127.0.0.1:$FLASK_PORT -w $FLASK_WORKERS --timeout $FLASK_TIMEOUT "main:create_app()" &
FLASK_PID=$!

echo "Flask PID: $FLASK_PID"

# Wait for Flask to be ready (with timeout)
echo "Waiting for Flask to become healthy..."
ELAPSED=0
INTERVAL=2

while [ $ELAPSED -lt $STARTUP_TIMEOUT ]; do
    # Check if Flask process is still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "Flask process died unexpectedly"
        exit 1
    fi

    # Check Flask health endpoint
    if curl -s http://127.0.0.1:$FLASK_PORT/health/ping > /dev/null 2>&1; then
        echo "Flask is healthy on port $FLASK_PORT"
        break
    fi

    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    echo "  Waiting... ($ELAPSED/$STARTUP_TIMEOUT seconds)"
done

# Check if we timed out
if [ $ELAPSED -ge $STARTUP_TIMEOUT ]; then
    echo "Flask failed to start within $STARTUP_TIMEOUT seconds"
    kill $FLASK_PID 2>/dev/null || true
    exit 1
fi

echo "=========================================="
echo "Flask ready. Starting Next.js on port $PORT..."
echo "=========================================="

# Cleanup function to kill Flask when script exits
cleanup() {
    echo "Shutting down Flask (PID: $FLASK_PID)..."
    kill $FLASK_PID 2>/dev/null || true
    wait $FLASK_PID 2>/dev/null || true
    echo "Cleanup complete"
}

# Register cleanup on script exit
trap cleanup EXIT INT TERM

# Start Next.js in foreground (PORT is set by Heroku)
cd frontend && npm start -- -p $PORT
