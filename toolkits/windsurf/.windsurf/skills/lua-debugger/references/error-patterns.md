# Lua Error Patterns

## Pattern Catalog

### 1. `attempt to call a nil value`

**Full error**: `lua: script.lua:15: attempt to call a nil value (global 'unpack')`

**Cause**: Aseprite uses Lua 5.3+ where `unpack` was moved to `table.unpack`.

**Fix**: Replace `unpack(...)` with `table.unpack(...)`:
```lua
-- WRONG
local r, g, b, a = unpack(pixel)

-- CORRECT
local r, g, b, a = table.unpack(pixel)
```

---

### 2. `attempt to index a nil value`

**Full error**: `lua: script.lua:8: attempt to index a nil value (local 'spr')`

**Cause**: A variable that was expected to be an object is nil. Common causes:
- `app.activeSprite` is nil (no sprite opened)
- Layer name not found
- Frame index out of range

**Fix**: Add nil checks:
```lua
local spr = app.activeSprite
if not spr then return "Error: No active sprite" end

local layer = spr.layers[1]
if not layer then return "Error: No layers found" end
```

For layer-by-name lookups:
```lua
local function find_layer(spr, name)
    for _, layer in ipairs(spr.layers) do
        if layer.name == name then return layer end
    end
    return nil
end

local layer = find_layer(spr, target_name)
if not layer then return "Error: Layer '" .. target_name .. "' not found" end
```

---

### 3. `bad argument #N to 'function'`

**Full error**: `lua: script.lua:12: bad argument #1 to 'image:getPixel' (value must be an integer)`

**Cause**: Wrong type passed to an Aseprite API function. Common type mismatches:
- String where number expected
- Float where integer expected
- Nil where object expected

**Fix**: Ensure correct types:
```lua
-- WRONG: string where number expected
img:getPixel("10", "20")

-- CORRECT: explicit integers
img:getPixel(10, 20)

-- WRONG: float where integer expected
img:getPixel(x + 0.5, y)

-- CORRECT: use math.floor for rounding
img:getPixel(math.floor(x + 0.5), math.floor(y + 0.5))
```

---

### 4. `cannot open file: No such file or directory`

**Full error**: `Cannot open file: /path/to/file.aseprite`

**Cause**: Path issues:
- Windows backslashes not converted to forward slashes
- File doesn't exist
- Path contains special characters not escaped for Lua

**Fix**:
```python
# In Python tool code:
esc = _lua_escape(filename.replace("\\", "/"))
# Use esc in Lua string: spr:saveAs("{esc}")
```

```lua
-- In Lua, always use forward slashes
local spr = app.open("C:/path/to/file.aseprite")  -- not "C:\path\..."
```

---

### 5. `script finished with errors`

**Full error**: `Aseprite script finished with errors`

**Cause**: Generic Aseprite error. The actual Lua error is in stderr. Check the full output for the specific error message.

**Fix**: Parse the output for the actual error:
```python
success, output = get_cli().execute_lua_script(script, filename)
if not success:
    # Look for Lua error patterns in output
    if "attempt to" in output:
        # nil value or type error
    elif "cannot open" in output:
        # file path error
    elif "bad argument" in output:
        # type mismatch
```

---

### 6. `No active sprite`

**Cause**: `app.activeSprite` is nil because no sprite was opened.

**Fix**: Pass the filename to `execute_lua_script` so Aseprite opens it:
```python
# CORRECT: Pass filename
success, output = get_cli().execute_lua_script(script, filename="sprite.aseprite")

# WRONG: No filename (app.activeSprite will be nil unless script opens one)
success, output = get_cli().execute_lua_script(script)
```

If creating a new sprite (no filename to open):
```lua
local spr = Sprite(32, 32)  -- creates and activates
-- or
local spr = app.open("template.aseprite")  -- open existing
```

---

### 7. Layer Not Found

**Full error**: Tool returns `"Error: Layer 'MyLayer' not found"`

**Cause**: Layer name is case-sensitive and must match exactly.

**Fix**:
- Check exact layer name with `sprite_list_layers` or `get_sprite_info`
- Use `set_layer` with `create_if_missing=True` to auto-create layers
- Remember: Aseprite layer names are case-sensitive

---

### 8. Frame Index Out of Range

**Full error**: Tool returns `"Error: Frame index 5 out of range (1-4)"`

**Cause**: Frame indices are 1-based in the Aseprite Lua API and in MCP tools.

**Fix**:
- Frame 1 = first frame (not frame 0)
- Check frame count: `#spr.frames`
- Use `add_frames` to add more frames before accessing them

---

### 9. Color Format Error

**Full error**: Tool returns `"Error: Invalid color format. Expected #RRGGBB"`

**Cause**: Color must be a hex string like `#ff0000`, not `red`, `rgb(255,0,0)`, or `0xff0000`.

**Fix**: Use `#RRGGBB` format:
```python
# CORRECT
draw_pixels_at(filename="sprite.aseprite", pixels=[{"x": 5, "y": 3, "color": "#ff0000"}])

# WRONG
draw_pixels_at(filename="sprite.aseprite", pixels=[{"x": 5, "y": 3, "color": "red"}])
draw_pixels_at(filename="sprite.aseprite", pixels=[{"x": 5, "y": 3, "color": "255,0,0"}])
```

---

### 10. Path Traversal Error

**Full error**: Tool returns `"Error: filename must not contain '..' (path traversal)"`

**Cause**: Security check prevents directory traversal attacks.

**Fix**: Use absolute or relative paths without `..`:
```python
# CORRECT
create_canvas(width=32, height=32, filename="sprites/hero.aseprite")

# WRONG
create_canvas(width=32, height=32, filename="../other/hero.aseprite")
```

---

### 11. Timeout Error

**Full error**: Script execution exceeds 60-second timeout.

**Cause**: Complex Lua script taking too long (e.g., pixel-by-pixel operations on large sprites).

**Fix**:
- Reduce sprite size
- Use batch operations instead of per-pixel loops
- Use Aseprite's built-in drawing commands instead of manual pixel iteration
- Break into multiple smaller operations

---

### 12. `attempt to perform arithmetic on a nil value`

**Cause**: Trying to do math on a variable that is nil. Often happens when:
- `img:getPixel()` returns nil (coordinates out of bounds)
- A lookup function returns nil instead of a number

**Fix**: Check for nil before arithmetic:
```lua
local pixel = img:getPixel(x, y)
if pixel == nil then
    return "Error: Pixel out of bounds at (" .. x .. "," .. y .. ")"
end
local r = app.pixelColor.rgba(pixel)
```

---

### 13. `attempt to compare nil with number`

**Cause**: Comparing a nil value against a number. Often from missing frame or layer lookups.

**Fix**: Validate lookups before comparisons:
```lua
local frame = spr.frames[frame_idx]
if not frame then
    return "Error: Frame " .. frame_idx .. " not found"
end
```

---

### 14. `stack overflow`

**Cause**: Infinite recursion in Lua script. Often from:
- Recursive function without base case
- Circular references in table traversal

**Fix**: Ensure all recursive functions have proper termination conditions.

---

### 15. `malformed number near`

**Cause**: Lua trying to parse a string as a number. Often from:
- Unescaped special characters in embedded strings
- Path with backslashes not properly escaped

**Fix**: Use `_lua_escape()` for all user-provided strings embedded in Lua:
```python
esc = _lua_escape(user_input)
script = f'local name = "{esc}"'
```