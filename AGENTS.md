# AGENTS.md

## Project overview

Aseprite MCP server — bridges LLMs to Aseprite via the Model Context Protocol. Two modes: CLI batch (`aseprite -b --script`) and real-time WebSocket drawing.

## Architecture

- **Entry point**: `aseprite_mcp.__main__:main` (registered as `aseprite-mcp` console script)
- **Server**: `aseprite_mcp/server.py` — FastMCP server with tools, resources, and prompts
- **CLI wrapper**: `aseprite_mcp/aseprite_cli.py` — runs `aseprite -b --script <tmpfile>` via subprocess
- **WebSocket bridge**: `aseprite_mcp/websocket_bridge.py` — launches Aseprite GUI with a Lua WS client
- **Lua generators**: `aseprite_mcp/lua_scripts.py` — generates Lua scripts for batch ops
- **Config**: `aseprite_mcp/config.py` — env vars (`ASEPRITE_PATH`, `ASEPRITE_WS_HOST`, `ASEPRITE_WS_PORT`, `ASEPRITE_OUTPUT_DIR`)

## Aseprite Lua version

Aseprite uses **Lua 5.3+** where `unpack` is `table.unpack`. Using the global `unpack` will error with "attempt to call a nil value".

## Commands

```bash
# Install
uv sync

# Install with dev deps
uv sync --extra dev

# Run tests
uv run pytest tests/ -v

# Lint
uv run ruff check src/ tests/

# Typecheck
uv run mypy src/

# Run server (stdio)
uv run aseprite-mcp

# Run server (HTTP)
uv run aseprite-mcp --transport streamable-http --port 8080
```

## Docker

Multi-stage build: `base` (OS + Aseprite) → `builder` (installs Python deps into system Python via `uv`) → `runtime` (copies installed packages + app source). No `.venv` or `uv` in the final image.

```bash
docker compose build
docker compose up -d          # HTTP mode on :8080, WS on :8765
docker compose run --rm aseprite-mcp stdio  # stdio mode
```

Runtime uses Xvfb (`DISPLAY=:99`). The entrypoint script (`docker-entrypoint.sh`) accepts `stdio` or `http [port]`.

Generated assets volume: `./generated_assets:/app/generated_assets`.

## MCP HTTP session flow

The streamable-http transport requires session management:
1. `POST /mcp` with `initialize` → response includes `mcp-session-id` header
2. `POST /mcp` with `notifications/initialized` + session header → 202
3. `POST /mcp` with `tools/call` + session header → response (SSE stream)

Required headers: `Content-Type: application/json`, `Accept: application/json, text/event-stream`, `mcp-session-id: <from step 1>`.

## Key gotchas

- **No Aseprite binary = hard failure**: `ASEPRITE_PATH` must be set or `aseprite` found on `$PATH`. The server raises `FileNotFoundError` at startup if missing.
- **Batch scripts are temporary**: `AsepriteCLI.run_batch` writes Lua to a temp file, runs it, then deletes it. Scripts must complete within 60s timeout.
- **`script_execute` returns raw stdout**: `AsepriteCLI.run_script` returns `result.stdout.decode()`. JSON-returning scripts (`run_json_script`) look for lines starting with `JSON_START` or `{`.
- **WebSocket tools need a running bridge**: `draw_pixels` and `fill_rect` require `ws_connect` to be called first. They send commands over a WebSocket to a running Aseprite instance.
- **`sprite_create` defaults output**: If `output_path` is empty, it auto-generates a filename in `output_dir` (default: `generated_assets/`).
- **`fill_rect` color format**: Takes a hex string like `#ff0000`, not separate RGBA values.
- **All sprite paths must end in supported extensions**: `.ase`, `.aseprite`, `.png`, `.gif`, `.jpg`, `.jpeg`, `.bmp`, `.webp` — enforced by `validate_sprite_path`.

## Test structure

Tests mock `subprocess.run` / `subprocess.Popen` — no Aseprite binary needed. Tests live in `tests/` with `pytest-asyncio` (async mode: `auto`).