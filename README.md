# Aseprite MCP Server

An MCP (Model Context Protocol) server that bridges LLMs to [Aseprite](https://www.aseprite.org/) for programmatic pixel art creation. Supports both CLI batch mode and real-time WebSocket drawing.

## Features

- **Sprite Management**: Create, export, copy, and inspect sprites
- **Drawing Tools**: Pixels, lines, rectangles, circles, polygons, paths, flood fill, and gradients
- **Animation**: Frame and cel management, tweening (linear and eased), oscillation, opacity animation, and propagation
- **Layer Operations**: Add, set, show/hide, set opacity, and copy layers between sprites
- **Palette Management**: Read/write palettes, remap colors across cel ranges
- **Pixel Reading**: Sample individual pixels or rectangular regions
- **Transforms**: Flip, rotate, resize, and crop sprites
- **Quality Assurance**: Validate scenes, audit for overlaps and out-of-range activity, sanitize animations
- **Spritesheet Export**: Generate spritesheets with JSON atlas metadata
- **Real-time Drawing**: WebSocket bridge for interactive pixel manipulation
- **Custom Lua Scripts**: Execute arbitrary Lua scripts in Aseprite
- **Preview Server**: HTTP server for browser preview of exported sprites
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

Output directory for generated assets (sprites, PNGs, spritesheets):

```bash
export ASEPRITE_OUTPUT_DIR=generated_assets  # default: generated_assets/ in CWD
```

Or use `--output-dir /path/to/assets` CLI flag. The directory is auto-created on first use.

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
--output-dir PATH                    Directory for generated assets (default: generated_assets/)
```

## MCP Tools

### Legacy Tools (server.py)

These use the original `run_json_script` / `run_batch` / `run_script` patterns:

| Tool | Description |
|------|-------------|
| `sprite_create` | Create a new sprite (saves to `output_dir` by default) |
| `sprite_export` | Export a sprite to PNG, GIF, etc. |
| `sprite_info` | Get metadata (dimensions, layers, tags, frames, palette) as JSON |
| `sprite_list_layers` | List all layers in a sprite |
| `sprite_list_tags` | List all frame tags in a sprite |
| `spritesheet_export` | Export as spritesheet with JSON atlas |
| `script_execute` | Run a custom Lua script |
| `ws_connect` | Launch Aseprite with WebSocket bridge |
| `draw_pixels` | Draw pixels on active sprite via WebSocket |
| `fill_rect` | Fill a rectangle on active sprite via WebSocket |

### Canvas (`tools/canvas.py`)

| Tool | Description |
|------|-------------|
| `create_canvas` | Create a new sprite with specified dimensions |
| `add_layer` | Add a named layer to a sprite |
| `add_frame` | Add a new frame |
| `set_frame` | Set active frame by 1-based index |
| `set_frame_duration` | Set duration of a specific frame (ms) |
| `set_layer` | Set active layer by name (optionally create it) |

### Drawing (`tools/drawing.py`)

| Tool | Description |
|------|-------------|
| `draw_pixels` | Draw multiple pixels on the active cel |
| `draw_line` | Draw a line with configurable thickness |
| `draw_rectangle` | Draw an outline or filled rectangle |
| `fill_area` | Flood-fill from a point |
| `draw_circle` | Draw an outline or filled circle/ellipse |
| `draw_pixels_at` | Draw pixels on a specific layer/frame |
| `draw_line_at` | Draw a line on a specific layer/frame |
| `draw_rectangle_at` | Draw a rectangle on a specific layer/frame |
| `draw_circle_at` | Draw a circle on a specific layer/frame |
| `fill_area_at` | Flood-fill on a specific layer/frame |
| `draw_polygon` | Draw a polygon on a specific layer/frame |
| `draw_path` | Draw a polyline path on a specific layer/frame |
| `apply_gradient_rect` | Apply a linear gradient fill to a rectangle |

### Animation (`tools/animation.py`)

| Tool | Description |
|------|-------------|
| `add_frames` | Add multiple frames with optional duration |
| `set_frame_duration_all` | Set duration for all frames |
| `set_layer_visibility` | Show or hide a layer by name |
| `set_layer_opacity` | Set layer opacity (0-255) |
| `get_sprite_info` | Get structured sprite info (dimensions, frames, layers) |
| `duplicate_frame_range` | Duplicate a range of frames |
| `set_cel_position` | Set a cel's position on a specific layer/frame |
| `tween_cel_positions` | Interpolate cel positions linearly across frames |
| `offset_cel_positions` | Offset cel positions by a delta across frames |
| `create_cel` | Create an empty cel on a layer/frame |
| `clear_cel` | Delete a cel on a layer/frame |
| `copy_cel` | Copy a cel between frames on the same layer |
| `copy_frame` | Copy all cels from one frame to another |
| `propagate_frame_to_range` | Copy a frame's cels to a range of frames |
| `set_tag` | Create or update an animation tag (with direction) |
| `tween_cel_positions_eased` | Tween cel positions with easing functions |
| `oscillate_cel_positions` | Sine-wave oscillation of cel positions |
| `tween_cel_opacity_eased` | Tween cel opacity with easing functions |
| `propagate_cels` | Copy cels across specific layers and frame range |

### Export (`tools/export.py`)

| Tool | Description |
|------|-------------|
| `export_sprite` | Export sprite to PNG, GIF, etc. via CLI `--save-as` |
| `copy_sprite` | Copy sprite to a new .aseprite file |

### Palette (`tools/palette.py`)

| Tool | Description |
|------|-------------|
| `get_palette` | Get the color palette as hex color list |
| `set_palette` | Set palette from a list of hex colors |
| `remap_colors_in_cel_range` | Replace colors in cels across a frame range |

### Pixel Read (`tools/pixel_read.py`)

| Tool | Description |
|------|-------------|
| `get_pixel_color` | Read the RGBA color at a single pixel |
| `get_pixels_rect` | Read all pixels in a rectangular region |

### Preview (`tools/preview.py`)

| Tool | Description |
|------|-------------|
| `start_preview_server` | Start an HTTP server for browser preview |
| `stop_preview_server` | Stop the preview server |

### Scene (`tools/scene.py`)

| Tool | Description |
|------|-------------|
| `copy_layers_between_sprites` | Copy named layers from one sprite to another |

### Guide (`tools/guide.py`)

| Tool | Description |
|------|-------------|
| `animation_workflow_guide` | Return a text guide for animation workflows |

### Quality (`tools/quality.py`)

| Tool | Description |
|------|-------------|
| `ensure_layers_present` | Create missing cels for specified layer/frame combos |
| `validate_scene` | Check for missing layers and cels |
| `audit_animation` | Audit for overlaps and out-of-range layer activity |
| `animation_sanitize` | Validate and fix animation consistency issues |

### Transform (`tools/transform.py`)

| Tool | Description |
|------|-------------|
| `flip_layer` | Flip a cel horizontally or vertically |
| `rotate_layer` | Rotate a cel by 90, 180, or 270 degrees |
| `resize_canvas` | Resize sprite (scales all content) |
| `crop_canvas` | Crop sprite to a specified region |

## MCP Resources

- `aseprite://sprites/{path}` - Sprite metadata
- `aseprite://palettes/{name}` - Built-in palette data (`dawnbringer32`, `pico8`)

## MCP Prompts

- `pixel_art_asset_gen` - Template for LLM-guided pixel art generation

## Integration Guide

### Quick Reference

| Tool | Config Key | Config Path | stdio | HTTP | Notes |
|------|-----------|-------------|:-----:|:----:|-------|
| Claude Desktop | `mcpServers` | `~/Library/Application Support/Claude/claude_desktop_config.json` | Y | N | Must restart after config change |
| VS Code Copilot | `servers` | `.vscode/mcp.json` | Y | Y | Agent mode required; VS Code 1.99+ |
| Claude Code | `mcpServers` | `.mcp.json` or `claude mcp add` | Y | Y | 3 scopes: local/project/user |
| Cursor | `mcpServers` | `~/.cursor/mcp.json` | Y | SSE | Global config only |
| opencode | `mcp` | `opencode.json` | Y | Y | Uses `type: "local"/"remote"`, `command` as array |
| Windsurf | `mcpServers` | `~/.codeium/windsurf/mcp_config.json` | Y | Y | `${env:VAR}` interpolation; max 100 tools |
| Cline | `mcpServers` | VS Code global state (UI) | Y | SSE | Configured via extension UI |
| Continue | `mcpServers` | `~/.continue/config.json` | Y | SSE | Inside existing config.json |
| Zed | `context_servers` | Zed `settings.json` | Y | Y | **Different key name!** |

Below are config snippets for each tool in three variants:

- **Local (uv run)** — running from a source checkout
- **Installed** — `aseprite-mcp` installed globally via `pip` or `uv tool`
- **Docker** — running inside a container

Replace `/path/to/aseprite-mcp-python` and `/path/to/aseprite` with your actual paths.

---

### Claude Desktop

**Config file:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

Claude Desktop only supports stdio transport. You must fully quit and restart the app after editing the config.

**Local (uv run):**

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Installed:**

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

**Docker:**

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

---

### VS Code (GitHub Copilot)

**Config file:** `.vscode/mcp.json` in your workspace root

Requires VS Code 1.99+ and Agent mode in Copilot Chat. Organization admins must enable the "MCP servers in Copilot" policy for Business/Enterprise users.

**Local (uv run):**

```json
{
  "servers": {
    "aseprite": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Installed:**

```json
{
  "servers": {
    "aseprite": {
      "command": "aseprite-mcp",
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Docker:**

```json
{
  "servers": {
    "aseprite": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "aseprite-mcp", "stdio"]
    }
  }
}
```

**HTTP (connect to a running server):**

Start the server first: `docker run --rm -p 8080:8080 -p 8765:8765 aseprite-mcp http 8080`

Then in VS Code `settings.json`:

```json
{
  "servers": {
    "aseprite": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

---

### Claude Code (CLI)

**Config file:** `.mcp.json` in project root, or `~/.claude.json` for user scope

You can also use the CLI:

```bash
# stdio (from source)
claude mcp add --transport stdio aseprite -- uv run --directory /path/to/aseprite-mcp-python aseprite-mcp

# stdio (installed)
claude mcp add --transport stdio aseprite -- aseprite-mcp

# HTTP
claude mcp add --transport http aseprite http://localhost:8080/mcp
```

Or manually in `.mcp.json`:

```json
{
  "mcpServers": {
    "aseprite": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Docker:**

```json
{
  "mcpServers": {
    "aseprite": {
      "type": "stdio",
      "command": "docker",
      "args": ["run", "--rm", "-i", "aseprite-mcp", "stdio"]
    }
  }
}
```

**HTTP:**

```json
{
  "mcpServers": {
    "aseprite": {
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

---

### Cursor

**Config file:** `~/.cursor/mcp.json`

Cursor supports stdio and SSE transports. Config is global (not per-project).

**Local (uv run):**

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Installed:**

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

**Docker:**

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

**SSE/HTTP (remote):**

```json
{
  "mcpServers": {
    "aseprite": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

---

### opencode

**Config file:** `opencode.json` in project root

opencode uses a different schema: `type: "local"` for stdio, `type: "remote"` for HTTP, and `command` as an array (not `command` string + `args` array). Environment variables use `{env:VAR}` interpolation.

**Local (uv run):**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "aseprite": {
      "type": "local",
      "command": ["uv", "run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "enabled": true,
      "environment": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Installed:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "aseprite": {
      "type": "local",
      "command": ["aseprite-mcp"],
      "enabled": true,
      "environment": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Docker:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "aseprite": {
      "type": "local",
      "command": ["docker", "run", "--rm", "-i", "aseprite-mcp", "stdio"],
      "enabled": true
    }
  }
}
```

**HTTP (remote):**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "aseprite": {
      "type": "remote",
      "url": "http://localhost:8080/mcp",
      "enabled": true
    }
  }
}
```

---

### Windsurf

**Config file:** `~/.codeium/windsurf/mcp_config.json`

Windsurf supports `${env:VAR}` and `${file:/path}` interpolation in commands and args. Remote servers use `serverUrl` (not `url`). Max 100 MCP tools total.

**Local (uv run):**

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Installed:**

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "aseprite-mcp",
      "env": {
        "ASEPRITE_PATH": "${env:ASEPRITE_PATH}"
      }
    }
  }
}
```

**Docker:**

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

**HTTP (remote):**

```json
{
  "mcpServers": {
    "aseprite": {
      "serverUrl": "http://localhost:8080/mcp"
    }
  }
}
```

---

### Cline (VS Code Extension)

**Config:** Managed through the Cline extension UI — click the MCP icon in the sidebar, then "Edit MCP Settings". Paste JSON directly into the settings.

**Local (uv run):**

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Installed:**

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

**Docker:**

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

---

### Continue (VS Code / JetBrains Extension)

**Config file:** `~/.continue/config.json`

The `mcpServers` key goes inside the existing `config.json` alongside other Continue settings.

**Local (uv run):**

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Installed:**

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

**Docker:**

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

---

### Zed Editor

**Config file:** Zed `settings.json` (open via Settings → Edit Settings)

Zed uses **`context_servers`** (not `mcpServers`). This is the only tool with a different top-level key.

**Local (uv run):**

```json
{
  "context_servers": {
    "aseprite": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/aseprite-mcp-python", "aseprite-mcp"],
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Installed:**

```json
{
  "context_servers": {
    "aseprite": {
      "command": "aseprite-mcp",
      "env": {
        "ASEPRITE_PATH": "/usr/bin/aseprite"
      }
    }
  }
}
```

**Docker:**

```json
{
  "context_servers": {
    "aseprite": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "aseprite-mcp", "stdio"]
    }
  }
}
```

**HTTP (remote):**

```json
{
  "context_servers": {
    "aseprite": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

---

### JetBrains AI

JetBrains IDEs (IntelliJ, PyCharm, WebStorm, etc.) currently act as an **MCP server** (exposing IDE capabilities to external clients), not an MCP consumer. To use Aseprite MCP with a JetBrains AI assistant, connect JetBrains to an external client (like Claude Desktop or Copilot) that has the Aseprite MCP server configured.

Alternatively, use the JetBrains terminal to run:

```bash
aseprite-mcp --transport stdio
```

and pipe it to your preferred AI tool.

## Architecture

The server is organized into a modular `tools/` package:

- **Entry point**: `aseprite_mcp.__main__:main`
- **Server**: `aseprite_mcp/server.py` -- FastMCP server hosting legacy tools, resources, and prompts
- **Tool modules**: `aseprite_mcp/tools/` -- 11 domain modules, each registering tools via `@mcp.tool()` decorators. Auto-imported by `__init__.py`
- **CLI wrapper**: `aseprite_mcp/aseprite_cli.py` -- subprocess runner with `execute_lua_script()` method
- **WebSocket bridge**: `aseprite_mcp/websocket_bridge.py`
- **Lua generators**: `aseprite_mcp/lua_scripts.py`
- **Config**: `aseprite_mcp/config.py`

New tools use `execute_lua_script()` which returns a `(success, output)` tuple. Most mutations are wrapped in `app.transaction()` for undo grouping. Frame indices are 1-based (Aseprite Lua convention). Colors use `#RRGGBB` hex strings. Layers are targeted by name.

## Development

```bash
uv sync --extra dev
uv run pytest tests/ -v
uv run ruff check src/ tests/
uv run mypy src/
```

### Test files

- `tests/test_aseprite_cli.py` -- CLI wrapper and `execute_lua_script` tests
- `tests/test_lua_scripts.py` -- Lua script generation tests
- `tests/test_server.py` -- legacy MCP tool tests
- `tests/test_websocket_bridge.py` -- WebSocket bridge tests
- `tests/test_config.py` -- configuration tests
- `tests/test_utils.py` -- utility tests
- `tests/test_main.py` -- entry point tests

All tests mock `subprocess.run`/`subprocess.Popen` -- no Aseprite binary needed.

## License

MIT
