# Common Fixes

## Fix Procedures for Frequent Issues

### Fix 1: `unpack` → `table.unpack`

**Symptom**: `attempt to call a nil value (global 'unpack')`

**Before**:
```lua
local r, g, b, a = unpack(pixel)
local args = unpack(params)
```

**After**:
```lua
local r, g, b, a = table.unpack(pixel)
local args = table.unpack(params)
```

**Scope**: All Lua scripts in `aseprite_mcp/lua_scripts.py` and tool modules.

---

### Fix 2: Nil Sprite Check

**Symptom**: `attempt to index a nil value (local 'spr')`

**Before**:
```lua
local spr = app.activeSprite
local w = spr.width
```

**After**:
```lua
local spr = app.activeSprite
if not spr then
    return "Error: No active sprite"
end
local w = spr.width
```

**Scope**: All tools that use `app.activeSprite`.

---

### Fix 3: Nil Layer Check

**Symptom**: `attempt to index a nil value` when accessing layer properties

**Before**:
```lua
local layer = find_layer(spr, layer_name)
local cel = layer:cel(frame_idx)
```

**After**:
```lua
local layer = find_layer(spr, layer_name)
if not layer then
    return "Error: Layer '" .. layer_name .. "' not found"
end
local cel = layer:cel(frame_idx)
```

**Scope**: All tools that look up layers by name.

---

### Fix 4: Nil Cel Check

**Symptom**: `attempt to index a nil value` when accessing cel properties

**Before**:
```lua
local cel = layer:cel(frame_idx)
local img = cel.image
```

**After**:
```lua
local cel = layer:cel(frame_idx)
if not cel then
    return "Error: No cel on layer '" .. layer_name .. "' at frame " .. frame_idx
end
local img = cel.image
```

**Scope**: All tools that access cel data.

---

### Fix 5: Path Normalization

**Symptom**: `cannot open file` or `malformed number near`

**Before** (Python):
```python
script = f'spr:saveAs("{filename}")'
```

**After** (Python):
```python
esc = _lua_escape(filename.replace("\\", "/"))
script = f'spr:saveAs("{esc}")'
```

**Scope**: All tools that embed filenames in Lua strings.

---

### Fix 6: Integer Coordinates

**Symptom**: `bad argument #1 to 'image:getPixel' (value must be an integer)`

**Before**:
```lua
local px = img:getPixel(x + dx, y + dy)
```

**After**:
```lua
local px = img:getPixel(math.floor(x + dx), math.floor(y + dy))
```

**Scope**: All tools that compute pixel coordinates (drawing, pixel_read).

---

### Fix 7: Frame Index Validation

**Symptom**: Frame index out of range

**Before**:
```lua
local frame = spr.frames[frame_idx]
```

**After**:
```lua
if frame_idx < 1 or frame_idx > #spr.frames then
    return "Error: Frame index " .. frame_idx .. " out of range (1-" .. #spr.frames .. ")"
end
local frame = spr.frames[frame_idx]
```

**Scope**: All tools that accept frame indices.

---

### Fix 8: Color Format Validation

**Symptom**: Invalid color format error

**Before** (Python):
```python
color = user_input  # might be "red" or "255,0,0"
```

**After** (Python):
```python
rgb = validate_hex_color(color)
if rgb is None:
    return "Error: Invalid color format. Expected #RRGGBB"
r, g, b = rgb
```

**Scope**: All tools that accept color parameters.

---

### Fix 9: Transaction Wrapping

**Symptom**: Aseprite shows "Cannot modify sprite outside transaction" or changes not grouped for undo

**Before**:
```lua
spr:newFrame()
spr:newLayer("test")
```

**After**:
```lua
app.transaction(function()
    spr:newFrame()
    spr:newLayer("test")
end)
```

**Scope**: All tools that modify sprite state.

---

### Fix 10: Save After Mutation

**Symptom**: Changes not persisted to file

**Before**:
```lua
app.transaction(function()
    -- mutations
end)
-- No save!
```

**After**:
```lua
app.transaction(function()
    -- mutations
end)
spr:saveAs(esc_path)
return "Success: changes saved"
```

**Scope**: All tools that modify sprites and take a filename parameter.

---

### Fix 11: Lua String Escaping

**Symptom**: `malformed number near` or `unfinished string`

**Before** (Python):
```python
script = f'local name = "{layer_name}"'
```

**After** (Python):
```python
esc = _lua_escape(layer_name)
script = f'local name = "{esc}"'
```

**Scope**: All tools that embed user-provided strings in Lua.

---

### Fix 12: Image Lock for Pixel Access

**Symptom**: `cannot modify locked image` or pixel operations fail silently

**Before**:
```lua
local img = cel.image
img:drawPixel(10, 20, color)
```

**After**:
```lua
local img = cel.image
img:clear()
-- Or use app.useTool{} for drawing operations
-- Or ensure the image is from a writable cel
```

**Note**: Aseprite images from `cel.image` are writable. Images from `Image(imgSpec)` need `img:drawPixel()` which works on new images. If you get lock errors, create a new Image and assign it to the cel.

---

### Fix 13: Output Parsing

**Symptom**: Tool returns unexpected output format

**Before** (Python):
```python
success, output = get_cli().execute_lua_script(script, filename)
return output  # raw output, might include debug prints
```

**After** (Python):
```python
success, output = get_cli().execute_lua_script(script, filename)
if success:
    # Parse expected output format
    for line in output.strip().split('\n'):
        if line.startswith('RESULT:'):
            return line[7:]
    return f"Success: {filename}"
return f"Failed: {output}"
```

**Scope**: All tools that need to parse Aseprite output.

---

### Fix 14: Boolean Conversion

**Symptom**: Lua `true`/`false` not converting properly to Python

**Before**:
```lua
return tostring(spr.transparent)
```

**After**:
```lua
if spr.transparent then
    print("transparent:true")
else
    print("transparent:false")
end
```

**Scope**: All tools that return boolean values from Lua.

---

### Fix 15: Empty Cel Handling

**Symptom**: `attempt to index a nil value` when accessing empty cel

**Before**:
```lua
local cel = layer:cel(frame_idx)
local x = cel.position.x
```

**After**:
```lua
local cel = layer:cel(frame_idx)
if cel then
    local x = cel.position.x
else
    -- Create an empty cel first
    cel = Cel(Image(imgSpec))
    layer:addCel(cel, spr.frames[frame_idx])
    local x = cel.position.x
end
```

**Scope**: All tools that access cel position or image on potentially empty frames.