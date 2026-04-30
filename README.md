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

| Tool | Description |
|------|-------------|
| `sprite_create` | Create a new sprite (saves to `output_dir` by default) |
| `sprite_export` | Export a sprite to PNG, GIF, etc. (saves to `output_dir` by default) |
| `sprite_info` | Get metadata (dimensions, layers, tags, frames, palette) |
| `sprite_list_layers` | List all layers in a sprite |
| `sprite_list_tags` | List all frame tags in a sprite |
| `spritesheet_export` | Export as spritesheet with JSON atlas (saves to `output_dir` by default) |
| `script_execute` | Run a custom Lua script |
| `ws_connect` | Launch Aseprite with WebSocket bridge |
| `draw_pixels` | Draw pixels on active sprite via WebSocket |
| `fill_rect` | Fill a rectangle on active sprite via WebSocket |

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

## Development

```bash
uv sync --extra dev
uv run pytest tests/ -v
uv run ruff check src/ tests/
uv run mypy src/
```

## License

MIT
