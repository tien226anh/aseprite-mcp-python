#!/bin/sh
set -e

mode="${1:-stdio}"

start_xvfb() {
    if command -v xvfb-run >/dev/null 2>&1; then
        echo "Starting Xvfb on display :99..."
        Xvfb :99 -screen 0 1024x768x24 &
        sleep 1
    fi
}

case "$mode" in
    stdio)
        exec uv run aseprite-mcp --transport stdio
        ;;
    http)
        port="${2:-8080}"
        start_xvfb
        exec uv run aseprite-mcp --transport streamable-http --port "$port"
        ;;
    *)
        echo "Usage: docker run <image> [stdio|http [port]]"
        echo "  stdio  - MCP server over STDIO (default)"
        echo "  http   - MCP server over HTTP with WebSocket support"
        exit 1
        ;;
esac