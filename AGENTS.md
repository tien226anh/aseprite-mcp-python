# AGENTS.md

## Project overview

Aseprite MCP server -- bridges LLMs to Aseprite via the Model Context Protocol. Two modes: CLI batch (`aseprite -b --script`) and real-time WebSocket drawing. The server exposes 57 tools across 11 domain-specific modules plus 10 legacy tools in `server.py` (67 total).

## Architecture

- **Entry point**: `aseprite_mcp.__main__:main` (registered as `aseprite-mcp` console script)
- **MCP server singleton**: `aseprite_mcp/__init__.py` creates `mcp = FastMCP("aseprite-mcp")`. All tool modules import `from aseprite_mcp import mcp` and register tools via `@mcp.tool()`.
- **Server**: `aseprite_mcp/server.py` -- FastMCP server with resources, prompts, and legacy tools (sprite_create, sprite_export, sprite_info, sprite_list_layers, sprite_list_tags, spritesheet_export, script_execute, ws_connect, draw_pixels, fill_rect). Also holds module-level singletons (`_get_cli()`, `_get_config()`, `_get_ws_bridge()`) that tool modules access via `_helpers`.
- **Tool modules**: `aseprite_mcp/tools/` -- 11 domain-specific modules auto-registered on import via `__init__.py`
  - `canvas.py` -- sprite creation, layer/frame management
  - `drawing.py` -- pixel, line, rectangle, circle, fill, polygon, path, gradient
  - `animation.py` -- frame ops, layer visibility/opacity, cel management, tweening, tags, propagation
  - `export.py` -- sprite export and copy
  - `palette.py` -- get/set palette, color remapping
  - `pixel_read.py` -- read pixel colors and rectangular regions
  - `preview.py` -- HTTP preview server for exported sprites
  - `scene.py` -- cross-sprite layer copying
  - `guide.py` -- animation workflow guides (pure text, no Aseprite interaction)
  - `quality.py` -- validation, audit, sanitization
  - `transform.py` -- flip, rotate, resize, crop
- **Helper utilities**: `aseprite_mcp/tools/_helpers.py` -- shared `get_cli()`, `get_config()`, `check_file()`, `validate_hex_color()`, `_lua_escape()`
- **CLI wrapper**: `aseprite_mcp/aseprite_cli.py` -- runs `aseprite -b --script <tmpfile>` via subprocess; includes `execute_lua_script()` method returning `(success, output)` tuple
- **WebSocket bridge**: `aseprite_mcp/websocket_bridge.py` -- launches Aseprite GUI with a Lua WS client
- **Lua generators**: `aseprite_mcp/lua_scripts.py` -- generates Lua scripts for legacy batch ops
- **Config**: `aseprite_mcp/config.py` -- env vars (`ASEPRITE_PATH`, `ASEPRITE_WS_HOST`, `ASEPRITE_WS_PORT`, `ASEPRITE_OUTPUT_DIR`)
- **Utilities**: `aseprite_mcp/utils.py` -- legacy validation helpers (`parse_hex_color`, `validate_dimensions`, `validate_color_mode`, `validate_sprite_path`)

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

Multi-stage build: `base` (OS + Aseprite) -> `builder` (installs Python deps into system Python via `uv`) -> `runtime` (copies installed packages + app source). No `.venv` or `uv` in the final image.

```bash
docker compose build
docker compose up -d          # HTTP mode on :8080, WS on :8765
docker compose run --rm aseprite-mcp stdio  # stdio mode
```

Runtime uses Xvfb (`DISPLAY=:99`). The entrypoint script (`docker-entrypoint.sh`) accepts `stdio` or `http [port]`.

Generated assets volume: `./generated_assets:/app/generated_assets`.

## MCP HTTP session flow

The streamable-http transport requires session management:
1. `POST /mcp` with `initialize` -> response includes `mcp-session-id` header
2. `POST /mcp` with `notifications/initialized` + session header -> 202
3. `POST /mcp` with `tools/call` + session header -> response (SSE stream)

Required headers: `Content-Type: application/json`, `Accept: application/json, text/event-stream`, `mcp-session-id: <from step 1>`.

## Complete tool list

### Legacy tools (server.py)

These use the older `run_json_script`, `run_batch`, and `run_script` patterns:

| Tool | Description |
|------|-------------|
| `sprite_create` | Create a new sprite (JSON output via `run_json_script`) |
| `sprite_export` | Export sprite to PNG/GIF/etc. |
| `sprite_info` | Get sprite metadata (dimensions, layers, tags, frames, palette) |
| `sprite_list_layers` | List all layers in a sprite |
| `sprite_list_tags` | List all frame tags in a sprite |
| `spritesheet_export` | Export spritesheet with JSON atlas metadata |
| `script_execute` | Run custom Lua script (raw stdout via `run_script`) |
| `ws_connect` | Launch Aseprite with WebSocket bridge |
| `draw_pixels` | Draw pixels via WebSocket (requires `ws_connect`) |
| `fill_rect` | Fill rectangle via WebSocket (requires `ws_connect`) |

### Canvas (canvas.py)

| Tool | Description |
|------|-------------|
| `create_canvas` | Create new sprite with dimensions and filename |
| `add_layer` | Add a named layer to a sprite |
| `add_frame` | Add a new frame to a sprite |
| `set_frame` | Set active frame by 1-based index |
| `set_frame_duration` | Set duration of a specific frame in ms |
| `set_layer` | Set active layer by name, optionally creating it |

### Drawing (drawing.py)

| Tool | Description |
|------|-------------|
| `draw_pixels` | Draw multiple pixels on active cel |
| `draw_line` | Draw a line on active cel (with thickness) |
| `draw_rectangle` | Draw a rectangle on active cel (outline or filled) |
| `fill_area` | Flood-fill from a point on active cel |
| `draw_circle` | Draw a circle on active cel (outline or filled) |
| `draw_pixels_at` | Draw pixels on a specific layer/frame |
| `draw_line_at` | Draw a line on a specific layer/frame |
| `draw_rectangle_at` | Draw a rectangle on a specific layer/frame |
| `draw_circle_at` | Draw a circle on a specific layer/frame |
| `fill_area_at` | Flood-fill on a specific layer/frame |
| `draw_polygon` | Draw a polygon on a specific layer/frame |
| `draw_path` | Draw a polyline path on a specific layer/frame |
| `apply_gradient_rect` | Apply a linear gradient fill to a rectangle |

### Animation (animation.py)

| Tool | Description |
|------|-------------|
| `add_frames` | Add multiple frames with optional duration |
| `set_frame_duration_all` | Set duration for all frames |
| `set_layer_visibility` | Show/hide a layer by name |
| `set_layer_opacity` | Set layer opacity (0-255) |
| `get_sprite_info` | Get structured sprite info (dimensions, frames, layers) |
| `duplicate_frame_range` | Duplicate a range of frames |
| `set_cel_position` | Set a cel's position on a layer/frame |
| `tween_cel_positions` | Linear interpolation of cel positions across frames |
| `offset_cel_positions` | Offset cel positions by delta across frames |
| `create_cel` | Create an empty cel on a layer/frame |
| `clear_cel` | Delete a cel on a layer/frame |
| `copy_cel` | Copy a cel between frames on the same layer |
| `copy_frame` | Copy all cels from one frame to another |
| `propagate_frame_to_range` | Copy a frame's cels to a range of frames |
| `set_tag` | Create or update an animation tag (with direction) |
| `tween_cel_positions_eased` | Tween with easing (linear, ease_in, ease_out, ease_in_out, smoothstep) |
| `oscillate_cel_positions` | Sine-wave oscillation of cel positions |
| `tween_cel_opacity_eased` | Tween cel opacity with easing |
| `propagate_cels` | Copy cels from a source frame across specific layers and frame range |

### Export (export.py)

| Tool | Description |
|------|-------------|
| `export_sprite` | Export sprite to PNG, GIF, etc. via CLI `--save-as` |
| `copy_sprite` | Copy sprite to a new .aseprite file |

### Palette (palette.py)

| Tool | Description |
|------|-------------|
| `get_palette` | Get color palette as hex color list |
| `set_palette` | Set palette from list of hex colors |
| `remap_colors_in_cel_range` | Replace source colors with target colors across cels |

### Pixel Read (pixel_read.py)

| Tool | Description |
|------|-------------|
| `get_pixel_color` | Read RGBA color at a single pixel |
| `get_pixels_rect` | Read all pixels in a rectangular region |

### Preview (preview.py)

| Tool | Description |
|------|-------------|
| `start_preview_server` | Start HTTP server for browser preview of exported sprites |
| `stop_preview_server` | Stop the preview HTTP server |

### Scene (scene.py)

| Tool | Description |
|------|-------------|
| `copy_layers_between_sprites` | Copy named layers (with cels) from one sprite to another |

### Guide (guide.py)

| Tool | Description |
|------|-------------|
| `animation_workflow_guide` | Return a text guide for pixel-art animation workflows |

### Quality (quality.py)

| Tool | Description |
|------|-------------|
| `ensure_layers_present` | Create missing empty cels for specified layers across a frame range |
| `validate_scene` | Check for missing layers and cels, returns JSON report |
| `audit_animation` | Audit for overlaps and out-of-range layer activity, returns JSON |
| `animation_sanitize` | Validate and optionally fix animation issues (reorder, create cels, handle out-of-range) |

### Transform (transform.py)

| Tool | Description |
|------|-------------|
| `flip_layer` | Flip a layer's cel horizontally or vertically |
| `rotate_layer` | Rotate a layer's cel by 90, 180, or 270 degrees |
| `resize_canvas` | Resize sprite (scales all content) |
| `crop_canvas` | Crop sprite to a specified region |

## Adding a new tool

Follow this pattern when adding a tool to an existing module (or creating a new one):

1. **In the tool module** (e.g., `src/aseprite_mcp/tools/canvas.py`):
   ```python
   from aseprite_mcp import mcp
   from aseprite_mcp.tools._helpers import _lua_escape, check_file, get_cli

   @mcp.tool()
   async def my_tool(filename: str, ...) -> str:
       """One-line description.

       Args:
           filename: Path to the Aseprite file
           ...
       """
       # 1. Validate inputs (return "Error: ..." strings, never raise)
       err = check_file(filename)
       if err:
           return err
       if ".." in filename:
           return "Error: filename must not contain '..' (path traversal)"

       # 2. Escape strings for Lua injection
       esc = _lua_escape(filename.replace("\\", "/"))

       # 3. Build Lua script as f-string
       script = f"""
   local spr = app.activeSprite
   if not spr then return "No active sprite" end

   app.transaction(function()
       -- mutations here
   end)

   spr:saveAs("{esc}")
   return "Success message"
   """

       # 4. Execute and return result
       success, output = get_cli().execute_lua_script(script, filename)
       if success:
           return f"Success: {filename}"
       return f"Failed to my_tool: {output}"
   ```

2. **If creating a new module**, register it in `src/aseprite_mcp/tools/__init__.py`:
   ```python
   from . import my_new_module  # noqa: F401
   ```

3. **Add tests** in `tests/test_tools_<module>.py` following the test patterns below.

## Key gotchas

- **No Aseprite binary = hard failure**: `ASEPRITE_PATH` must be set or `aseprite` found on `$PATH`. The server raises `FileNotFoundError` at startup if missing.
- **Batch scripts are temporary**: `AsepriteCLI.run_batch` writes Lua to a temp file, runs it, then deletes it. Scripts must complete within 60s timeout.
- **`execute_lua_script()` returns a tuple**: New tool modules use `get_cli().execute_lua_script(script, filename=None)` which returns `(success: bool, output: str)`. This is the primary way new tools interact with Aseprite. The `success` flag is `True` when the subprocess exits with code 0 and no error markers in output.
- **Two ways to open sprites in Lua**:
  - **With filename**: `get_cli().execute_lua_script(script, filename)` — Aseprite opens the file as a CLI arg, so `app.activeSprite` is set. Most tools use this.
  - **Without filename**: `get_cli().execute_lua_script(script)` — Script must call `app.open("path")` itself. Used by tools that create new sprites (e.g., `create_canvas`) or open multiple sprites (e.g., `copy_layers_between_sprites`).
- **`app.transaction(function() ... end)` pattern**: Most new tools wrap mutations in `app.transaction()` for undo-grouped operations in Aseprite.
- **Frame indices are 1-based**: The Aseprite Lua API uses 1-based indexing. All new tools that accept frame indices use 1-based numbers. This matches the Lua convention (`spr.frames[1]` is the first frame).
- **Pixel coordinates are 0-based**: While frame indices are 1-based, pixel coordinates (x, y) are 0-based, matching the Aseprite image API (`img:getPixel(0, 0)` is top-left).
- **Color format for new tools**: Hex strings like `#RRGGBB` (e.g., `#ff0000`). The `_helpers.validate_hex_color()` function parses these to `(r, g, b)` tuples for Lua injection. Legacy `fill_rect` also uses hex strings.
- **Two color validation systems** (don't confuse them):
  - `_helpers.validate_hex_color(color)` — returns `(r, g, b)` tuple or `None`. Used by new tool modules. No alpha.
  - `utils.parse_hex_color(color)` — returns `(r, g, b, a)` tuple or raises `ValueError`. Used by legacy server.py tools. Includes alpha.
- **Layer targeting: by name string**: New tools find layers by name string, not index. If a layer name is not found, the tool returns an error. Some tools offer `create_if_missing` to auto-create layers.
- **Path traversal protection**: Filenames containing `..` are rejected by several tools (create_canvas, copy_layers_between_sprites, flip_layer, rotate_layer, resize_canvas, crop_canvas, ensure_layers_present, etc.) to prevent directory traversal attacks.
- **Windows backslash handling**: Always normalize file paths with `filename.replace("\\", "/")` before embedding in Lua strings. The `_esc_path()` helper in `animation.py` does this; consider using it or the same pattern.
- **`script_execute` returns raw stdout**: `AsepriteCLI.run_script` returns `result.stdout.decode()`. JSON-returning scripts (`run_json_script`) look for lines starting with `JSON_START` or `{`. This pattern is only used by legacy tools.
- **WebSocket tools need a running bridge**: `draw_pixels` and `fill_rect` in server.py require `ws_connect` to be called first. They send commands over a WebSocket to a running Aseprite instance. These are separate from the similarly-named `draw_pixels` and `fill_area` in the drawing module, which work via CLI batch mode.
- **`sprite_create` defaults output**: If `output_path` is empty, it auto-generates a filename in `output_dir` (default: `generated_assets/`).
- **All sprite paths must end in supported extensions**: `.ase`, `.aseprite`, `.png`, `.gif`, `.jpg`, `.jpeg`, `.bmp`, `.webp` -- enforced by `validate_sprite_path`.
- **Lua escape helper**: `_lua_escape()` in `_helpers.py` escapes double quotes, backslashes, newlines, carriage returns, and null bytes in strings embedded in Lua scripts to prevent injection.
- **Error handling convention**: Tools return error strings (e.g., `"Error: ..."`, `"Failed to ...: {output}"`), never raise exceptions. Validate inputs early, then call `execute_lua_script` and check the `success` flag.
- **Lua output parsing**: New tools parse Aseprite output from the `output` string. Common patterns:
  - `return "message"` — the return value appears in stdout
  - `print("KEY:value")` — custom key-value markers (e.g., `PIXEL:r,g,b,a`, `ERROR:msg`)
  - `print(table.concat(parts))` — JSON array output (e.g., palette tools)

## Test structure

Tests mock `subprocess.run` / `subprocess.Popen` -- no Aseprite binary needed. Tests live in `tests/` with `pytest-asyncio` (async mode: `auto`).

### Test patterns

**Standard fixture pattern** (used in all tool test files):
```python
@pytest.fixture
def mock_cli():
    cli = MagicMock(spec=AsepriteCLI)
    cli.execute_lua_script.return_value = (True, "Success")
    return cli

@pytest.fixture(autouse=True)
def patch_get_cli(mock_cli):
    with patch("aseprite_mcp.tools.<module>.get_cli", return_value=mock_cli):
        yield mock_cli
```

**Key testing conventions**:
- Use `@pytest.mark.asyncio` on all async test methods
- Organize tests into `TestXxx` classes by tool function
- Test validation errors first (invalid inputs), then success cases, then failure cases
- For `check_file` patching: `with patch("aseprite_mcp.tools.<module>.check_file", return_value=None):`
- Assert on both the result string AND the Lua script content: `script = mock_cli.execute_lua_script.call_args[0][0]`
- E2E tests (`test_e2e_knight_quest.py`) import ALL tool modules at the top so `patch()` can resolve dotted paths at runtime

### Test files

- `tests/test_aseprite_cli.py` -- CLI wrapper and `execute_lua_script` tests
- `tests/test_lua_scripts.py` -- Lua script generation tests
- `tests/test_server.py` -- legacy MCP tool tests
- `tests/test_websocket_bridge.py` -- WebSocket bridge tests
- `tests/test_config.py` -- configuration tests
- `tests/test_utils.py` -- utility tests
- `tests/test_helpers.py` -- `_helpers` module tests
- `tests/test_main.py` -- entry point tests
- `tests/test_tools_canvas.py` -- canvas tool tests
- `tests/test_tools_animation.py` -- animation tool tests
- `tests/test_tools_export.py` -- export tool tests
- `tests/test_tools_palette.py` -- palette tool tests
- `tests/test_tools_pixel_read.py` -- pixel read tool tests
- `tests/test_tools_preview.py` -- preview server tests
- `tests/test_tools_transform.py` -- transform tool tests
- `tests/test_e2e_knight_quest.py` -- end-to-end workflow tests (mocked)
- `tests/test_e2e_knight_quest_live.py` -- live E2E tests (requires Aseprite binary)
- `tests/test_integration_knight_quest.py` -- integration tests (mocked)
- `tests/test_integration_knight_quest_live.py` -- live integration tests