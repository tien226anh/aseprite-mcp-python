---
name: lua-debugger
description: 'Debug and fix Aseprite Lua scripts for MCP tools. Use when: a tool returns "Failed to ..." or "Error: ..." output; Lua scripts have nil value errors, path issues, or API misuse; interpreting execute_lua_script failure output; fixing Lua 5.3 compatibility issues; debugging Aseprite batch mode errors; troubleshooting tool implementation bugs in the aseprite-mcp-python project.'
argument-hint: 'error message or Lua script to debug, e.g. "attempt to call nil value" or "Failed to draw_circle: Error in script"'
user-invocable: true
---

# Lua Debugger

Debug and fix Aseprite Lua scripts used in MCP tools. This skill covers interpreting error output, recognizing common Lua 5.3 and Aseprite API error patterns, and applying systematic fixes.

## When to Use

- A tool returns `"Failed to ..."` or `"Error: ..."` output
- `execute_lua_script` returns `(False, error_output)`
- Lua scripts throw nil value errors
- Path issues with Windows backslashes or special characters
- Aseprite API misuse (wrong method names, wrong argument types)
- Lua 5.3 compatibility issues (e.g., `unpack` vs `table.unpack`)
- Debugging tool implementation bugs in the aseprite-mcp project

## Debugging Workflow

```
INTERPRET → ISOLATE → FIX → VERIFY → PREVENT
```

### 1. INTERPRET — Read the Error

`execute_lua_script` returns `(success, output)`. When `success=False`:
- The `output` string contains Aseprite's stderr/stdout
- Look for Lua error patterns (see [error-patterns.md](./references/error-patterns.md))
- Common markers: `attempt to`, `bad argument`, `runtime error`

### 2. ISOLATE — Find the Cause

- Identify the **error line** from the stack trace
- Check the **variable type** at that line (nil? wrong type?)
- Check the **function call** (exists? correct args?)
- Check the **path** (backslashes? special chars? file exists?)

### 3. FIX — Apply the Correction

See [common-fixes.md](./references/common-fixes.md) for specific fix patterns.

### 4. VERIFY — Test the Fix

- Re-run the tool with the same parameters
- Check `success=True` and expected output
- For tools that modify sprites, read back the result to confirm

### 5. PREVENT — Add Safeguards

- Add nil checks before accessing properties
- Use `_lua_escape()` for all user-provided strings
- Normalize paths with `replace("\\", "/")`
- Validate inputs before building Lua scripts

## Quick Error Lookup

| Error Pattern | Cause | Fix |
|--------------|-------|-----|
| `attempt to call a nil value` | Function doesn't exist in Lua 5.3 | Use `table.unpack` not `unpack` |
| `attempt to index a nil value` | Variable is nil | Add nil check or verify sprite/layer exists |
| `bad argument #1 to 'fn'` | Wrong type passed | Check Aseprite API expects (see [api-gotchas.md](./references/api-gotchas.md)) |
| `cannot open file` | Path issue | Normalize backslashes, check file exists |
| `script finished with errors` | Generic Aseprite error | Check stderr for specific Lua error |
| `No active sprite` | `app.activeSprite` is nil | Pass filename to `execute_lua_script` |
| Layer not found | Layer name mismatch | Check exact layer name (case-sensitive) |
| Frame out of range | Frame index too high | Use 1-based indexing, check frame count |

## Debugging Tools

### Read the Lua Script
When debugging a tool, read the generated Lua script:
```python
# In test: capture the script
script = mock_cli.execute_lua_script.call_args[0][0]
print(script)  # inspect the generated Lua
```

### Test Lua Directly
Use `script_execute` to test Lua snippets:
```python
script_execute(lua_code="""
local spr = app.open("test.aseprite")
if not spr then return "Failed to open" end
print("Sprite: " .. spr.width .. "x" .. spr.height)
""")
```

### Read Back Sprite State
Use `get_sprite_info` or `sprite_info` to verify sprite state after operations.

## Reference Files

- [error-patterns.md](./references/error-patterns.md) — Complete error pattern catalog with causes and fixes
- [common-fixes.md](./references/common-fixes.md) — Step-by-step fix procedures for common issues
- [api-gotchas.md](./references/api-gotchas.md) — Aseprite Lua API pitfalls and correct usage
- [debug-checklist.md](./references/debug-checklist.md) — Systematic debugging checklist