# Aseprite MCP Server

An MCP (Model Context Protocol) server that bridges LLMs to [Aseprite](https://www.aseprite.org/) for programmatic pixel art creation. Supports both CLI batch mode and real-time WebSocket drawing.

## Features

- **Sprite Management**: Create, export, and inspect sprites via CLI batch mode
- **Spritesheet Export**: Generate spritesheets with JSON atlas metadata
- **Real-time Drawing**: WebSocket bridge for interactive pixel manipulation
- **Custom Lua Scripts**: Execute arbitrary Lua scripts in Aseprite
- **Built-in Palettes**: Dawnbringer32 and PICO-8 palettes included
- **Pixel Art Prompts**: Guided prompt template for LLM-driven asset generation

## Prerequisites

- [Aseprite](https://www.aseprite.org/) v1.2+ installed (or built from source)
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```bash
git clone <repo-url> && cd aseprite-mcp-python
uv sync
```

## Configuration

Set the path to your Aseprite binary via environment variable:

```bash
export ASEPRITE_PATH=/path/to/aseprite
```

Or pass it as a CLI argument (`--aseprite-path`).

Optional WebSocket settings:

```bash
export ASEPRITE_WS_HOST=127.0.0.1  # default
export ASEPRITE_WS_PORT=8765       # default
```

## Usage

### STDIO transport (for Claude Desktop, Cursor, etc.)

```bash
aseprite-mcp --transport stdio
```

### Streamable HTTP transport

```bash
aseprite-mcp --transport streamable-http --port 9090
```

### CLI options

```
--transport {stdio,streamable-http}  Transport protocol (default: stdio)
--port PORT                         HTTP port for streamable-http (default: 8080)
--aseprite-path PATH                Path to Aseprite binary
--ws-port PORT                      WebSocket port for bridge (default: 8765)
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `sprite_create` | Create a new sprite with given dimensions and color mode |
| `sprite_export` | Export a sprite to PNG, GIF, etc. |
| `sprite_info` | Get metadata (dimensions, layers, tags, frames, palette) |
| `sprite_list_layers` | List all layers in a sprite |
| `sprite_list_tags` | List all frame tags in a sprite |
| `spritesheet_export` | Export as spritesheet with JSON atlas |
| `script_execute` | Run a custom Lua script |
| `ws_connect` | Launch Aseprite with WebSocket bridge |
| `draw_pixels` | Draw pixels on active sprite via WebSocket |
| `fill_rect` | Fill a rectangle on active sprite via WebSocket |

## MCP Resources

- `aseprite://sprites/{path}` - Sprite metadata
- `aseprite://palettes/{name}` - Built-in palette data (`dawnbringer32`, `pico8`)

## MCP Prompts

- `pixel_art_asset_gen` - Template for LLM-guided pixel art generation

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/path/to/aseprite"
      }
    }
  }
}
```

Or if installed globally:

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "aseprite-mcp",
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

## Docker

A pre-built Docker image with Aseprite and Xvfb (for WebSocket mode) is included.

### Build

```bash
docker build -t aseprite-mcp .
```

### Run (STDIO mode)

```bash
docker run --rm -i aseprite-mcp stdio
```

### Run (HTTP mode)

```bash
docker run --rm -p 8080:8080 -p 8765:8765 aseprite-mcp http 8080
```

### Claude Desktop with Docker

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "aseprite-mcp", "stdio"]
    }
  }
}
```

### Docker Compose

```bash
docker compose up
```

This starts the MCP server in HTTP mode on port 8080 with WebSocket on 8765.

## Development

```bash
uv sync --extra dev
uv run pytest tests/ -v
uv run ruff check src/ tests/
uv run mypy src/
```

## License

MIT