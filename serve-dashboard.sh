#!/bin/bash

# Serve Dashboard Locally
# Starts a local server on port 8000 and opens the dashboard
#
# Usage:
#   ./serve-dashboard.sh           # Run in foreground (Ctrl+C to stop)
#   ./serve-dashboard.sh -b        # Run in background (survives terminal close)
#   ./serve-dashboard.sh --background

PORT=8000
BACKGROUND=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--background)
            BACKGROUND=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./serve-dashboard.sh [-b|--background]"
            exit 1
            ;;
    esac
done

# Kill any existing process on port 8000
echo "Checking for existing process on port $PORT..."
PID=$(lsof -ti :$PORT)
if [ -n "$PID" ]; then
    echo "Killing existing process (PID: $PID)..."
    kill -9 $PID
    sleep 1
fi

# Change to the script's directory (works regardless of where script is called from)
cd "$(dirname "$0")"

if [ "$BACKGROUND" = true ]; then
    # Start server in background with nohup (survives terminal close)
    echo "Starting local server in background on http://localhost:$PORT..."
    nohup python3 -m http.server $PORT > /dev/null 2>&1 &
    SERVER_PID=$!
    sleep 1
    echo "Opening dashboard in browser..."
    open "http://localhost:$PORT/dashboard.html"
    echo "Server running in background (PID: $SERVER_PID)"
    echo "To stop: kill $SERVER_PID  (or: pkill -f 'python3 -m http.server $PORT')"
else
    # Start server in foreground
    echo "Starting local server on http://localhost:$PORT..."
    python3 -m http.server $PORT &
    sleep 1
    echo "Opening dashboard in browser..."
    open "http://localhost:$PORT/dashboard.html"
    echo "Server running. Press Ctrl+C to stop."
    wait
fi
