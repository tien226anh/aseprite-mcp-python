---
description: "Use when: writing or modifying Aseprite MCP tool modules, Lua scripts, or tests. Covers error handling, Lua escaping, indexing, color validation, and tool implementation conventions."
name: "Aseprite MCP Conventions"
---

# Aseprite MCP Coding Conventions

## Error Handling — Never Raise in New Tools

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

## Lua Script Rules

### Use `table.unpack`, not `unpack`
Aseprite uses Lua 5.3+ where the global `unpack` is nil:
```lua
-- ✅ table.unpack(pixel)
-- ❌ unpack(pixel)  → "attempt to call a nil value"
```

### Wrap Mutations in `app.transaction()`
```lua
app.transaction(function()
    spr:newFrame()
    spr:newLayer("name")
end)
```

### Always Save After Mutations
```lua
spr:saveAs("path/to/file.aseprite")
```

### Account for Cel Position Offset
When using `img:drawPixel()` or `img:putPixel()`, subtract the cel's position:
```lua
local ox = cel.position.x
local oy = cel.position.y
img:drawPixel(x - ox, y - oy, color)
```

## Indexing Conventions

| What | Base | Example |
|------|------|---------|
| Frame indices | **1-based** | `spr.frames[1]` is the first frame |
| Pixel coordinates | **0-based** | `img:getPixel(0, 0)` is top-left |

## String Escaping — Always

1. **Normalize Windows backslashes** before embedding in Lua:
   ```python
   esc = _lua_escape(filename.replace("\\", "/"))
   ```
2. **Escape all user-provided strings** with `_lua_escape()` to prevent Lua injection.
3. The `animation.py` module has `_esc_path()` that combines both steps.

## Path Traversal Protection

Reject filenames containing `..`:
```python
if ".." in filename:
    return "Error: filename must not contain '..' (path traversal)"
```

## Color Validation — Don't Mix the Two Systems

| System | Function | Returns | Used In |
|--------|----------|---------|---------|
| New tools | `validate_hex_color(color)` | `(r, g, b)` or `None` | `tools/` modules |
| New tools (alpha) | `validate_hex_color_alpha(color)` | `(r, g, b, a)` or `None` | `tools/` modules |
| Legacy | `utils.parse_hex_color(color)` | `(r, g, b, a)` or **raises** `ValueError` | `server.py` only |

New tools use `validate_hex_color` — check for `None`, don't catch exceptions.

## Layer Targeting

Layers are found **by name string**, not by index. Names are case-sensitive.
Some tools offer `create_if_missing: bool` to auto-create missing layers.

## Two Ways to Open Sprites

- **With filename**: `execute_lua_script(script, filename)` — Aseprite opens the file, `app.activeSprite` is set. **Most tools use this.**
- **Without filename**: `execute_lua_script(script)` — Script must call `app.open("path")` itself. Only for tools that **create** new sprites or open multiple sprites.

## Python Source Conventions

- Add `from __future__ import annotations` at the top of every source file
- MyPy strict mode: all function parameters and return types need type annotations
- New tool modules must be registered in `src/aseprite_mcp/tools/__init__.py` with `# noqa: F401`
- Use `@mcp.tool()` decorator from `from aseprite_mcp import mcp`

## Testing

- Mock `AsepriteCLI` — no Aseprite binary needed
- Standard fixture: `mock_cli.execute_lua_script.return_value = (True, "Success")`
- Assert on **both** the result string AND the Lua script content:
  ```python
  script = mock_cli.execute_lua_script.call_args[0][0]
  assert "app.transaction" in script
  ```
- Patch `check_file` when testing success paths: `with patch("...check_file", return_value=None):`
- All async tests use `@pytest.mark.asyncio`