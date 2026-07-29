#!/bin/bash
# Start both Flask backend and Next.js frontend for local development
# Usage: ./scripts/dev.sh
# Use this script when Git Bash, WSL, or another shell that supports .sh files

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}Starting MyTools development servers...${NC}"

# Runaway-spawn guard: if a dev server's descendant process count blows past
# this, something is stuck in a retry loop (e.g. Turbopack failing to resolve
# a module and re-spawning a new postcss worker every attempt) rather than
# running normally. Kill everything instead of letting it pile up processes.
MAX_TREE_PROCESSES=20

# Collect a PID and all of its descendants (recursively), since `kill` on a
# parent PID does not kill children when job control isn't active - the
# backgrounded `cd frontend && npm run dev` subshell, npm, and the `next dev`
# process it spawns are all separate PIDs that survive a plain `kill $PID`.
# Uses `ps -ef` (not pgrep, which isn't available in Git Bash/Cygwin) - PID is
# column 2 and PPID is column 3 in the -ef format on Linux, macOS, and Cygwin.
process_tree_pids() {
    local pid=$1
    local pids=("$pid")
    local child
    for child in $(ps -ef | awk -v ppid="$pid" 'NR>1 && $3==ppid {print $2}'); do
        pids+=($(process_tree_pids "$child"))
    done
    echo "${pids[@]}"
}

kill_process_tree() {
    local pid=$1
    local tree_pids
    tree_pids=$(process_tree_pids "$pid")
    kill $tree_pids 2>/dev/null
}

# Kill child processes on exit
cleanup() {
    echo -e "\n${RED}Shutting down dev servers...${NC}"
    kill_process_tree "$FLASK_PID"
    kill_process_tree "$NEXT_PID"
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
cd ..

echo -e "${CYAN}Both servers running. Press Ctrl+C to stop.${NC}"

# Watch for either process exiting, or a runaway spawn from either process's
# tree, while both are up.
while kill -0 "$FLASK_PID" 2>/dev/null && kill -0 "$NEXT_PID" 2>/dev/null; do
    for pid in "$FLASK_PID" "$NEXT_PID"; do
        tree_count=$(process_tree_pids "$pid" | wc -w)
        if [ "$tree_count" -gt "$MAX_TREE_PROCESSES" ]; then
            echo -e "\n${RED}[Guard] Process tree for PID $pid has spawned $tree_count processes (limit: $MAX_TREE_PROCESSES).${NC}"
            echo -e "${YELLOW}[Guard] This usually means a build error is stuck retrying (e.g. a stale frontend/.next cache after a config change).${NC}"
            echo -e "${YELLOW}[Guard] Try: rm -rf frontend/.next${NC}"
            cleanup
        fi
    done
    sleep 1
done

echo -e "${RED}A server exited unexpectedly. Shutting down...${NC}"
cleanup
