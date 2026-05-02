---
inclusion: always
---

# Aseprite MCP Coding Conventions

## Error Handling — Never Raise
New tools return error strings, never raise exceptions. Validate inputs early, return `"Error: ..."` for invalid inputs.

## Lua Script Rules
- Use `table.unpack`, NOT `unpack` (Lua 5.3+)
- Wrap mutations in `app.transaction()`
- Always save after mutations: `spr:saveAs("path")`
- Account for cel position offset

## Indexing
- Frame indices: **1-based**, Pixel coordinates: **0-based**

## String Escaping
- Normalize Windows backslashes: `filename.replace("\\", "/")`
- Escape all user-provided strings with `_lua_escape()`

## Path Traversal
- Reject filenames containing `..`

## Color Validation — Two Systems, Don't Mix
- New tools: `validate_hex_color(color)` → `(r, g, b)` or `None`
- Legacy: `utils.parse_hex_color(color)` → raises `ValueError`

## Layer Targeting
- Layers found by **name string**, not index. Case-sensitive.

## Python Source Conventions
- `from __future__ import annotations` at the top of every source file
- MyPy strict: all function parameters and return types need type annotations

## Testing Patterns
- Mock `AsepriteCLI`, `@pytest.mark.asyncio`, assert on result + Lua script
