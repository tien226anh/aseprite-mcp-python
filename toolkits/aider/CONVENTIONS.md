# Aseprite MCP Coding Conventions for Aider

## Error Handling
- New tools return error strings, never raise exceptions
- Validate inputs early, return `"Error: ..."` for invalid inputs
- Check `success` flag from `execute_lua_script()`

## Lua Script Rules
- Use `table.unpack`, NOT `unpack` (Lua 5.3+)
- Wrap mutations in `app.transaction(function() ... end)`
- Always save after mutations: `spr:saveAs("path")`
- Account for cel position offset: `img:drawPixel(x - cel.position.x, y - cel.position.y, color)`

## Indexing
- Frame indices: **1-based** (`spr.frames[1]` is first frame)
- Pixel coordinates: **0-based** (`img:getPixel(0, 0)` is top-left)

## String Escaping
- Normalize Windows backslashes: `filename.replace("\\", "/")`
- Escape all user-provided strings with `_lua_escape()`

## Path Traversal
- Reject filenames containing `..`

## Color Validation
- Two systems, don't mix:
  - New tools: `validate_hex_color(color)` → `(r, g, b)` or `None`
  - Legacy: `utils.parse_hex_color(color)` → `(r, g, b, a)` or raises `ValueError`

## Layer Targeting
- Layers found by **name string**, not index. Case-sensitive.

## Python Source Conventions
- `from __future__ import annotations` at the top of every source file
- MyPy strict: all function parameters and return types need type annotations
- New tool modules registered in `src/aseprite_mcp/tools/__init__.py` with `# noqa: F401`

## Testing Patterns
- Mock `AsepriteCLI` — no Aseprite binary needed
- Standard fixture: `mock_cli.execute_lua_script.return_value = (True, "Success")`
- Assert on **both** the result string AND the Lua script content
- All async tests use `@pytest.mark.asyncio`
- Test order: validation errors → success cases → failure cases
