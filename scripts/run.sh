#!/bin/bash
# Start NOVA-SHIELD system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "========================================="
echo "Starting NOVA-SHIELD..."
echo "========================================="

# Check if running as root (required for PAM integration)
if [ "$EUID" -ne 0 ]; then 
    echo "[WARN] Not running as root. Some features may be limited."
    echo "For full functionality, run with: sudo ./scripts/run.sh"
fi

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start the dashboard in background
if [ "$1" != "--no-dashboard" ]; then
    echo "[START] Starting web dashboard..."
    python3 -m gui.dashboard &
    DASHBOARD_PID=$!
fi

# Start main daemon
echo "[START] Starting security daemon..."
python3 app/main.py

# Cleanup on exit
if [ ! -z "$DASHBOARD_PID" ]; then
    kill $DASHBOARD_PID
fi

echo "[OK] NOVA-SHIELD stopped"