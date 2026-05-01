---
description: "Use when: working on the aseprite-mcp-python project in any capacity — coding, testing, asset creation, agent/skill creation, or debugging. Covers project architecture, coding conventions, testing, asset workflows, agent orchestration, and customization layer conventions."
name: "Aseprite MCP Project Guide"
applyTo: "**"
---

# Aseprite MCP Project Guide

Comprehensive conventions and reference for the aseprite-mcp-python project.

## Project Overview

Aseprite MCP server — bridges LLMs to Aseprite via the Model Context Protocol. Two modes: CLI batch (`aseprite -b --script`) and real-time WebSocket drawing. The server exposes 67 tools across 11 domain modules + 10 legacy tools.

## Architecture

```
src/aseprite_mcp/
├── __init__.py          # MCP singleton: mcp = FastMCP("aseprite-mcp")
├── __main__.py          # Entry point: aseprite_mcp.__main__:main
├── server.py            # Legacy tools + module singletons (_get_cli, _get_config, _get_ws_bridge)
├── aseprite_cli.py      # CLI wrapper: runs aseprite -b --script <tmpfile>
├── config.py            # Env vars: ASEPRITE_PATH, ASEPRITE_WS_HOST, etc.
├── lua_scripts.py       # Legacy Lua script generators
├── utils.py             # Legacy validation helpers
├── websocket_bridge.py  # WebSocket bridge for real-time drawing
└── tools/
    ├── __init__.py      # Auto-imports all tool modules
    ├── _helpers.py      # Shared: get_cli, get_config, check_file, validate_hex_color, _lua_escape
    ├── animation.py     # Frame ops, tweening, tags, cel management
    ├── canvas.py         # Sprite creation, layer/frame management
    ├── drawing.py        # Pixel, line, rectangle, circle, fill, polygon, path, gradient
    ├── export.py         # Sprite export and copy
    ├── palette.py        # Get/set palette, color remapping
    ├── pixel_read.py     # Read pixel colors and regions
    ├── preview.py        # HTTP preview server
    ├── quality.py        # Validation, audit, sanitization
    ├── scene.py          # Cross-sprite layer copying
    ├── guide.py          # Animation workflow guides (text only)
    └── transform.py      # Flip, rotate, resize, crop
```

## Commands

```bash
uv sync                          # Install dependencies
uv sync --extra dev               # Install with dev deps
uv run pytest tests/ -v           # Run tests
uv run ruff check src/ tests/     # Lint
uv run mypy src/                  # Typecheck
uv run aseprite-mcp               # Run server (stdio)
uv run aseprite-mcp --transport streamable-http --port 8080  # HTTP mode
```

## Coding Conventions

### Error Handling — Never Raise in New Tools

New tools in `src/aseprite_mcp/tools/` **return error strings**, never raise exceptions:

```python
# ✅ Correct
if width <= 0:
    return f"Error: width must be > 0, got {width}"
err = check_file(filename)
if err:
    return err
success, output = get_cli().execute_lua_script(script, filename)
if success:
    return f"Success: {filename}"
return f"Failed to draw: {output}"

# ❌ Wrong (legacy server.py raises, new tools don't)
raise ValueError("Invalid input")
```

### Lua Script Rules

- **Use `table.unpack`, not `unpack`** — Lua 5.3+ removed the global `unpack`
- **Wrap mutations in `app.transaction()`** — for undo-grouped operations
- **Always save after mutations** — `spr:saveAs("path")`
- **Account for cel position offset** — `img:drawPixel(x - cel.position.x, y - cel.position.y, color)`

### Indexing

| What | Base | Example |
|------|------|---------|
| Frame indices | **1-based** | `spr.frames[1]` is the first frame |
| Pixel coordinates | **0-based** | `img:getPixel(0, 0)` is top-left |

### String Escaping

1. **Normalize Windows backslashes**: `filename.replace("\\", "/")`
2. **Escape all user-provided strings**: `_lua_escape()`
3. **Combined helper**: `_esc_path()` in `animation.py`

### Path Traversal Protection

```python
if ".." in filename:
    return "Error: filename must not contain '..' (path traversal)"
```

### Color Validation — Two Systems, Don't Mix

| System | Function | Returns | Used In |
|--------|----------|---------|---------|
| New tools | `validate_hex_color(color)` | `(r, g, b)` or `None` | `tools/` modules |
| New tools (alpha) | `validate_hex_color_alpha(color)` | `(r, g, b, a)` or `None` | `tools/` modules |
| Legacy | `utils.parse_hex_color(color)` | `(r, g, b, a)` or **raises** `ValueError` | `server.py` only |

### Layer Targeting

Layers are found **by name string**, not by index. Names are case-sensitive.

### Two Ways to Open Sprites

- **With filename**: `execute_lua_script(script, filename)` — most tools
- **Without filename**: `execute_lua_script(script)` — only for tools that create new sprites or open multiple sprites

### Python Source Conventions

- `from __future__ import annotations` at the top of every source file
- MyPy strict: all function parameters and return types need type annotations
- New tool modules registered in `src/aseprite_mcp/tools/__init__.py` with `# noqa: F401`
- Use `@mcp.tool()` decorator from `from aseprite_mcp import mcp`

## Testing

- Mock `AsepriteCLI` — no Aseprite binary needed
- Standard fixture: `mock_cli.execute_lua_script.return_value = (True, "Success")`
- Assert on **both** the result string AND the Lua script content
- Patch `check_file` when testing success paths: `with patch("...check_file", return_value=None):`
- All async tests use `@pytest.mark.asyncio`
- Test organization: `TestXxx` classes grouped by tool function
- Test order: validation errors → success cases → failure cases
- E2E tests import ALL tool modules at top so `patch()` can resolve dotted paths

## Asset Creation

### Pipeline

```
CONCEPT → CANVAS → PALETTE → LAYERS → DRAW → VERIFY → ANIMATE → TAG → VALIDATE → EXPORT
```

### Naming Conventions

| Pattern | Example |
|---------|---------|
| Filenames | `snake_case.aseprite` — `knight_idle.aseprite` |
| Character sprites | `{character}_{action}.aseprite` |
| Animation tags | `snake_case` — `idle`, `walk`, `melee_attack` |
| Layer names | `PascalCase` for body parts — `Body`, `Armor`, `Sword` |

### Directory Organization

```
generated_assets/{project_name}/
├── hero/           # Player characters
├── monsters/       # Enemies and NPCs
├── environment/    # Tiles, backgrounds, structures
├── effects/        # VFX, spells, impacts
└── cutscene/       # Story scenes, portraits
```

### Canvas Size Reference

| Asset Type | Typical Size | Frames |
|-----------|-------------|--------|
| Items/pickups | 16×16 to 24×24 | 1-4 |
| Small enemies | 16×16 to 24×24 | 4 |
| Player characters | 32×32 to 48×48 | 4-8 |
| Tiles | 16×16 or 32×32 | 1 |
| Backgrounds | 240×135 to 960×540 | 1-8 |
| VFX | 16×16 to 64×64 | 4-8 |

### Always Use `_at` Variants

Target specific layer+frame: `draw_pixels_at`, `draw_line_at`, `draw_circle_at`, etc.

### Read Back After Drawing

```python
get_pixels_rect(filename="hero.aseprite", x=0, y=0, width=32, height=32,
    layer_name="outline", frame_index=1)
```

## Agent Orchestration

The project has 9 specialized agents in `.github/agents/`:

| Agent | Role | Can Call |
|-------|------|----------|
| Asset Design Orchestrator | Coordinates full session | All 8 specialists |
| Character Designer | Character sprites | Animator, Asset Reviewer |
| Tile Designer | Tiles & environment | Animator, Asset Reviewer |
| VFX Designer | Effects & spells | Asset Reviewer |
| Background Designer | Parallax backgrounds | Animator, Asset Reviewer |
| Item Designer | Items & pickups | Animator, Asset Reviewer |
| Animator | Adds animation | Asset Reviewer |
| Asset Reviewer | Reviews & fixes | — |
| Asset Exporter | Exports & packages | — |

### Workflow

```
PLAN → DELEGATE → REVIEW → FIX → EXPORT
```

- **Parallel**: Independent assets (character + tileset) can be delegated simultaneously
- **Sequential**: Animation after base sprite; compositing after both assets; palette swaps after original reviewed

## Customization Layer Conventions

### Agents (`.github/agents/*.agent.md`)

- **Frontmatter**: `description`, `name`, `tools`, `agents`, `argument-hint`, `user-invocable`
- **Tools**: Include `'sequential-thinking/*'` and `'aseprite/*'` MCP tools on all design agents
- **Agents**: List sub-agents this agent can delegate to
- **Skills**: Reference relevant skills in a `## Skills` section in the body
- **Constraints**: Define what the agent should NOT do
- **Approach**: Step-by-step workflow

### Skills (`.github/skills/<name>/SKILL.md`)

- **Frontmatter**: `name` (must match folder), `description`, `argument-hint`, `user-invocable`
- **Progressive loading**: Keep SKILL.md under 500 lines; use `references/` for details
- **Relative paths**: Use `./references/file.md` for skill resources
- **Self-contained**: Include all procedural knowledge to complete the task

### Instructions (`.github/instructions/*.instructions.md`)

- **Frontmatter**: `description` (keyword-rich for discovery), `name`, `applyTo` (optional glob)
- **On-demand**: Loaded when the agent detects task relevance
- **Explicit**: `applyTo` loads when matching files are in context
- **One concern per file**: Separate files for different topics
- **Concise and actionable**: Every line should guide behavior