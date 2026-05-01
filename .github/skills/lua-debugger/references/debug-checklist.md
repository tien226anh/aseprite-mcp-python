# Debug Checklist

## Systematic Debugging Process

When a tool returns an error, follow this checklist in order:

### Phase 1: Interpret the Error

- [ ] **Read the full output** — Don't just look at the first line. The actual error may be buried in stderr.
- [ ] **Identify the error type** — Match against patterns in [error-patterns.md](./error-patterns.md):
  - `attempt to call a nil value` → Missing function (likely `unpack`)
  - `attempt to index a nil value` → Nil variable (sprite, layer, cel)
  - `bad argument #N` → Type mismatch
  - `cannot open file` → Path issue
  - `script finished with errors` → Generic (check stderr)
- [ ] **Find the line number** — Lua errors include `script.lua:LINE`. Map this to the generated Lua script.
- [ ] **Check if it's a Python validation error** — Some errors come from the Python tool code before Lua runs:
  - `"Error: filename must not contain '..'"` → Path traversal check
  - `"Error: Invalid color format"` → `validate_hex_color()` failed
  - `"Error: File not found"` → `check_file()` failed

### Phase 2: Isolate the Cause

- [ ] **Extract the Lua script** — In tests: `script = mock_cli.execute_lua_script.call_args[0][0]`
- [ ] **Find the failing line** — Match the line number from the error to the script
- [ ] **Check variable types** — Is the variable nil? Wrong type? Out of range?
- [ ] **Check function existence** — Does the function exist in Aseprite Lua 5.3?
- [ ] **Check path format** — Are there backslashes? Special characters? Is the file path correct?
- [ ] **Check frame/layer indices** — Are they 1-based? Within range?
- [ ] **Check color format** — Is it `#RRGGBB`? Not `rgb()` or named colors?

### Phase 3: Fix the Issue

- [ ] **Apply the appropriate fix** from [common-fixes.md](./common-fixes.md):
  - `unpack` → `table.unpack`
  - Nil sprite → Add nil check or pass filename
  - Nil layer → Add `find_layer` with nil check
  - Nil cel → Add nil check or create cel
  - Path issue → Normalize backslashes, use `_lua_escape()`
  - Type error → Use `math.floor()` for integers, check types
  - Frame range → Validate 1-based index, check `#spr.frames`
  - Color format → Use `validate_hex_color()`, embed as `app.pixelColor.rgba(r,g,b,a)`
- [ ] **Wrap mutations in `app.transaction()`** — If the fix involves sprite mutations
- [ ] **Add `spr:saveAs()` at the end** — If the tool modifies the sprite
- [ ] **Return a meaningful success/error message** — Not just `return "ok"`

### Phase 4: Verify the Fix

- [ ] **Re-run the tool** with the same parameters
- [ ] **Check `success=True`** — The `execute_lua_script` call should return `(True, output)`
- [ ] **Check the output content** — Does it contain the expected result?
- [ ] **Read back sprite state** — Use `get_sprite_info` or `get_pixel_color` to verify changes
- [ ] **Run the existing tests** — `uv run pytest tests/ -v`

### Phase 5: Prevent Recurrence

- [ ] **Add input validation** — Check for nil, wrong type, out of range before building Lua
- [ ] **Use `_lua_escape()`** — For all user-provided strings embedded in Lua
- [ ] **Normalize paths** — `filename.replace("\\", "/")` for all file paths
- [ ] **Add nil checks** — For sprite, layer, cel, frame lookups in Lua
- [ ] **Write a test** — Add a test case for the error scenario
- [ ] **Update error messages** — Make them descriptive and actionable

---

## Common Debug Scenarios

### Scenario: Tool Returns "Failed to ..."

```python
# Check what the actual error is
success, output = get_cli().execute_lua_script(script, filename)
if not success:
    # output contains the error details
    return f"Failed to {operation}: {output}"
```

**Steps**:
1. Look at the `output` string for the Lua error message
2. Match against error patterns
3. Fix the Lua script generation in the tool code

### Scenario: Tool Returns "Error: ..."

```python
# This is a Python validation error, not a Lua error
err = check_file(filename)
if err:
    return f"Error: {err}"
```

**Steps**:
1. Check which validation failed (file exists? path traversal? color format?)
2. Fix the input or the validation logic

### Scenario: Lua Script Runs But Produces Wrong Output

```python
success, output = get_cli().execute_lua_script(script, filename)
# success=True but output is unexpected
```

**Steps**:
1. Check the Lua script's `return` or `print()` statements
2. Verify the output parsing in the Python tool code
3. Add debug `print()` statements to the Lua script

### Scenario: Changes Not Persisted

```python
# Tool runs successfully but sprite file is unchanged
```

**Steps**:
1. Check that `spr:saveAs()` is called at the end of the Lua script
2. Verify the save path matches the expected output path
3. Check for path normalization issues (backslashes)

### Scenario: Test Failure

```python
# pytest test fails
```

**Steps**:
1. Check which assertion failed
2. If it's a Lua script assertion, inspect `mock_cli.execute_lua_script.call_args`
3. If it's a return value assertion, check the tool's error handling
4. Run with `-v` flag for detailed output: `uv run pytest tests/test_tools_xxx.py -v`

---

## Quick Reference: Error → Fix

| Error | Quick Fix |
|-------|-----------|
| `attempt to call a nil value (global 'unpack')` | Replace `unpack` with `table.unpack` |
| `attempt to index a nil value (local 'spr')` | Add nil check: `if not spr then return "Error: No sprite" end` |
| `attempt to index a nil value (local 'layer')` | Add nil check after `find_layer()` |
| `attempt to index a nil value (local 'cel')` | Add nil check or create empty cel |
| `bad argument #N to 'fn' (value must be an integer)` | Use `math.floor()` on computed coordinates |
| `cannot open file` | Normalize path: `filename.replace("\\", "/")` |
| `No active sprite` | Pass filename to `execute_lua_script(script, filename)` |
| Layer not found | Check exact name (case-sensitive), use `create_if_missing` |
| Frame out of range | Use 1-based indexing, check `#spr.frames` |
| Invalid color format | Use `#RRGGBB` format, validate with `validate_hex_color()` |
| Path traversal error | Remove `..` from paths |
| Timeout (>60s) | Reduce sprite size or use batch operations |
| Changes not saved | Add `spr:saveAs()` at end of Lua script |
| `malformed number near` | Use `_lua_escape()` for embedded strings |