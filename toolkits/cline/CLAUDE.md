# Aseprite MCP Project Guide

Aseprite MCP server — bridges LLMs to Aseprite via the Model Context Protocol. 67 tools across 11 domain modules + 10 legacy tools.

## Architecture
```
src/aseprite_mcp/
├── __init__.py          # MCP singleton
├── __main__.py          # Entry point
├── server.py            # Legacy tools
├── aseprite_cli.py      # CLI wrapper
├── config.py            # Env vars
└── tools/
    ├── _helpers.py      # Shared utilities
    ├── animation.py     # Frame ops, tweening, tags
    ├── canvas.py         # Sprite creation, layers
    ├── drawing.py        # Pixel, shapes, gradients
    ├── export.py         # Export and copy
    ├── palette.py        # Color management
    ├── pixel_read.py     # Read pixels
    ├── preview.py        # HTTP preview
    ├── quality.py        # Validation, audit
    ├── scene.py          # Cross-sprite copying
    ├── guide.py          # Workflow guides
    └── transform.py      # Flip, rotate, resize
```

## Commands
```bash
uv sync                          # Install dependencies
uv run pytest tests/ -v           # Run tests
uv run ruff check src/ tests/     # Lint
uv run mypy src/                  # Typecheck
uv run aseprite-mcp               # Run server (stdio)
```

## Coding Conventions

### Error Handling — Never Raise
New tools return error strings, never raise exceptions.

### Lua Script Rules
- Use `table.unpack`, NOT `unpack` (Lua 5.3+)
- Wrap mutations in `app.transaction()`
- Always save after mutations: `spr:saveAs("path")`
- Account for cel position offset

### Indexing
- Frame indices: **1-based**, Pixel coordinates: **0-based**

### String Escaping
- Normalize Windows backslashes: `filename.replace("\\", "/")`
- Escape all user-provided strings with `_lua_escape()`

### Path Traversal
- Reject filenames containing `..`

### Color Validation — Two Systems, Don't Mix
- New tools: `validate_hex_color(color)` → `(r, g, b)` or `None`
- Legacy: `utils.parse_hex_color(color)` → raises `ValueError`

### Layer Targeting
- Layers found by **name string**, not index. Case-sensitive.

## Asset Creation

### Pipeline
```
CONCEPT → CANVAS → PALETTE → LAYERS → DRAW → VERIFY → ANIMATE → TAG → VALIDATE → EXPORT
```

### Naming Conventions
- Filenames: `snake_case.aseprite`
- Character sprites: `{character}_{action}.aseprite`
- Layer names: PascalCase for body parts, Tags: snake_case

### Directory Organization
```
generated_assets/{project_name}/
├── hero/           # Player characters
├── monsters/       # Enemies and NPCs
├── environment/    # Tiles, backgrounds, structures
├── effects/        # VFX, spells, impacts
└── cutscene/       # Story scenes, portraits
```

### Canvas Sizes
| Asset Type | Typical Size | Frames |
|-----------|-------------|--------|
| Items/pickups | 16×16 to 24×24 | 1-4 |
| Small enemies | 16×16 to 24×24 | 4 |
| Player characters | 32×32 to 48×48 | 4-8 |
| Tiles | 16×16 or 32×32 | 1 |
| Backgrounds | 240×135 to 960×540 | 1-8 |
| VFX | 16×16 to 64×64 | 4-8 |

### Always Use `_at` Variants & Read Back After Drawing

### Animation Timing
| Animation | Duration | Frames | Easing |
|-----------|----------|--------|--------|
| Idle | 100-150ms | 4 | ease_in_out |
| Walk | 80-120ms | 8 | linear |
| Attack | 50-80ms | 4-6 | ease_in → ease_out |
| Float | 100-150ms | 4-8 | sine |

## Key Gotchas
- No Aseprite binary = hard failure
- `execute_lua_script()` returns `(success: bool, output: str)`
- Frame indices 1-based, pixel coordinates 0-based
- Color format: hex `#RRGGBB` for new tools
- Two color validation systems — don't mix
- Layer targeting: by name string, case-sensitive
- Path traversal: reject `..` in filenames
- Windows: always normalize backslashes
- Error handling: return strings, never raise

## Testing
- Mock `AsepriteCLI`, `@pytest.mark.asyncio`, assert on result + Lua script

## Sub-Agents
9 specialized sub-agents in `.claude/agents/`. Use `@agent-name`:
- `@asset-design-orchestrator`, `@character-designer`, `@tile-designer`, `@vfx-designer`, `@background-designer`, `@item-designer`, `@animator`, `@asset-reviewer`, `@asset-exporter`
