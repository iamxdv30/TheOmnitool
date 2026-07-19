#!/bin/bash
# Start both Flask backend and Next.js frontend for local development
# Usage: ./scripts/dev.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Starting MyTools development servers...${NC}"

# Kill child processes on exit
cleanup() {
    echo -e "\n${RED}Shutting down dev servers...${NC}"
    kill $FLASK_PID $NEXT_PID 2>/dev/null
    wait $FLASK_PID $NEXT_PID 2>/dev/null
    echo -e "${GREEN}All servers stopped.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start Flask backend
echo -e "${GREEN}[Backend]${NC} Starting Flask on http://localhost:5000"
python main.py &
FLASK_PID=$!

# Start Next.js frontend
echo -e "${GREEN}[Frontend]${NC} Starting Next.js on http://localhost:3000"
cd frontend && npm run dev &
NEXT_PID=$!

echo -e "${CYAN}Both servers running. Press Ctrl+C to stop.${NC}"

# Wait for either process to exit
wait -n $FLASK_PID $NEXT_PID
echo -e "${RED}A server exited unexpectedly. Shutting down...${NC}"
cleanup
