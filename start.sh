#!/bin/sh
set -e

start_xvfb() {
    if command -v xvfb-run >/dev/null 2>&1; then
        echo "Starting Xvfb on display :99..."
        Xvfb :99 -screen 0 1024x768x24 &
        sleep 1
    fi
}

start_xvfb
exec python -m aseprite_mcp --transport streamable-http --port 8080
