# Aseprite MCP Project

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
New tools return error strings, never raise exceptions. Validate inputs early, return `"Error: ..."` for invalid inputs.

### Lua Script Rules
- Use `table.unpack`, NOT `unpack` (Lua 5.3+)
- Wrap mutations in `app.transaction()`
- Always save after mutations: `spr:saveAs("path")`
- Account for cel position offset: `img:drawPixel(x - cel.position.x, y - cel.position.y, color)`

### Indexing
- Frame indices: **1-based** (`spr.frames[1]` is first frame)
- Pixel coordinates: **0-based** (`img:getPixel(0, 0)` is top-left)

### String Escaping
- Normalize Windows backslashes: `filename.replace("\\", "/")`
- Escape all user-provided strings with `_lua_escape()`

### Path Traversal
- Reject filenames containing `..`

### Color Validation — Two Systems, Don't Mix
- New tools: `validate_hex_color(color)` → `(r, g, b)` or `None`
- Legacy: `utils.parse_hex_color(color)` → `(r, g, b, a)` or raises `ValueError`

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
- Layer names: PascalCase for body parts
- Tags: snake_case

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

### Always Use `_at` Variants
Target specific layer+frame: `draw_pixels_at`, `draw_line_at`, `draw_circle_at`, etc.

### Read Back After Drawing
```python
get_pixels_rect(filename="hero.aseprite", x=0, y=0, width=32, height=32,
    layer_name="outline", frame_index=1)
```

### Animation Timing
| Animation | Duration | Frames | Easing |
|-----------|----------|--------|--------|
| Idle | 100-150ms | 4 | ease_in_out |
| Walk | 80-120ms | 8 | linear |
| Attack | 50-80ms | 4-6 | ease_in → ease_out |
| Float | 100-150ms | 4-8 | sine |
| VFX expand | 40-80ms | 4-8 | ease_out |

## Key Gotchas
- No Aseprite binary = hard failure: `ASEPRITE_PATH` must be set
- `execute_lua_script()` returns `(success: bool, output: str)`
- Frame indices are 1-based, pixel coordinates are 0-based
- Color format: hex `#RRGGBB` for new tools
- Two color validation systems — don't mix them
- Layer targeting: by name string, case-sensitive
- Path traversal: reject `..` in filenames
- Windows: always normalize backslashes
- Error handling: return strings, never raise

## Testing
- Mock `AsepriteCLI` — no Aseprite binary needed
- `@pytest.mark.asyncio` on all async tests
- Assert on both result string AND Lua script content

## Sub-Agents
This project has 9 specialized sub-agents in `.gemini/agents/`. Use `@agent-name` to invoke them:
- `@asset-design-orchestrator` — Coordinate full multi-asset sessions
- `@character-designer` — Create character sprites
- `@tile-designer` — Create tilesets
- `@vfx-designer` — Create VFX effects
- `@background-designer` — Create parallax backgrounds
- `@item-designer` — Create items and pickups
- `@animator` — Add animation to sprites
- `@asset-reviewer` — Review and fix quality issues
- `@asset-exporter` — Export and package assets
