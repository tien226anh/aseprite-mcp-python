---
name: lua-master
description: 'Write, review, and debug Lua scripts for Aseprite MCP tools. Use when: adding new tool functions to the aseprite_mcp project; writing Lua scripts embedded in Python f-strings; debugging Lua execution errors from Aseprite batch mode; understanding Aseprite Lua API patterns for sprites, layers, frames, cels, images, and palettes; fixing Lua 5.3 compatibility issues like table.unpack; escaping strings for Lua injection safety.'
argument-hint: 'action [write|review|debug] and description of the Lua task'
user-invocable: true
---

# Lua Master for Aseprite MCP

Write, review, and debug Lua scripts for the Aseprite MCP server tools. This skill covers the Lua scripting patterns used throughout the `aseprite_mcp` project, including the Aseprite Lua API, Python-Lua interop, and common pitfalls.

## When to Use

- Adding a new tool function that executes Lua in Aseprite
- Writing or modifying Lua scripts embedded in Python f-strings
- Debugging Lua execution errors from Aseprite batch mode
- Understanding Aseprite Lua API for sprites, layers, frames, cels, images, palettes
- Fixing Lua 5.3 compatibility issues (e.g., `table.unpack` vs `unpack`)
- Escaping strings for safe Lua injection
- Reviewing existing tool implementations for correctness

## Architecture Overview

All tool modules in `aseprite_mcp/tools/` follow the same pattern:

1. **Python function** decorated with `@mcp.tool()`
2. **Input validation** — return `"Error: ..."` strings, never raise exceptions
3. **String escaping** — `_lua_escape()` and `_esc_path()` for safe embedding
4. **Lua script** built as Python f-string
5. **Execution** via `get_cli().execute_lua_script(script, filename)` returning `(success, output)`
6. **Result parsing** — check `success` flag, parse `output` string

See [lua-patterns.md](./references/lua-patterns.md) for the full pattern reference.

## Critical Gotchas

| Gotcha | Details |
|--------|---------|
| **Lua 5.3+** | Aseprite uses Lua 5.3+. Use `table.unpack`, NOT `unpack` (which is nil) |
| **1-based indexing** | Frames: `spr.frames[1]` is first frame. Layers: `ipairs(spr.layers)`. Pixels: `img:getPixel(0,0)` is top-left (0-based) |
| **Path normalization** | Always `filename.replace("\\", "/")` before embedding in Lua strings |
| **String escaping** | Use `_lua_escape()` for user-provided strings, `_esc_path()` for filenames |
| **Error handling** | Return `"Error: ..."` strings from tools, never raise exceptions |
| **`app.transaction()`** | Wrap mutations in `app.transaction(function() ... end)` for undo grouping |
| **Filename vs no filename** | `execute_lua_script(script, filename)` opens the file as CLI arg (sets `app.activeSprite`). `execute_lua_script(script)` requires script to call `app.open("path")` itself |
| **`spr:saveAs()`** | Always save after mutations: `spr:saveAs("escaped_path")` |
| **Color format** | New tools use hex `#RRGGBB` parsed by `validate_hex_color()` to `(r,g,b)` tuple. Legacy tools use `parse_hex_color()` to `(r,g,b,a)` |
| **`img:putPixel` vs `img:drawPixel`** | `putPixel` sets pixel directly. `drawPixel` blends with alpha. Use `putPixel` for direct color, `drawPixel` for compositing |

## Tool Implementation Checklist

When adding a new tool, follow this checklist:

- [ ] Import `mcp`, `_lua_escape`, `check_file`, `get_cli` from appropriate modules
- [ ] Add `@mcp.tool()` decorator with descriptive docstring
- [ ] Validate all inputs early (return `"Error: ..."` for invalid inputs)
- [ ] Check for path traversal (`".." in filename`)
- [ ] Escape all strings with `_lua_escape()` before embedding in Lua
- [ ] Normalize paths with `filename.replace("\\", "/")`
- [ ] Use `app.transaction()` for mutations
- [ ] Save sprite with `spr:saveAs(escaped_path)` or `spr:saveAs(spr.filename)`
- [ ] Return meaningful success/failure messages
- [ ] Handle the `success` flag from `execute_lua_script()`
- [ ] Write tests in `tests/test_tools_<module>.py`

## Reference Files

- **Lua Patterns**: [lua-patterns.md](./references/lua-patterns.md) — Complete pattern reference for all tool types
- **Aseprite API**: [aseprite-api.md](./references/aseprite-api.md) — Key Aseprite Lua API objects and methods
- **Testing Guide**: [testing-guide.md](./references/testing-guide.md) — How to test Lua tool functions