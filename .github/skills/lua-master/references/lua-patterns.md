# Lua Script Patterns for Aseprite MCP Tools

## Standard Tool Pattern

Every tool follows this structure:

```python
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

## Opening Sprites: Two Patterns

### Pattern 1: With filename (most common)
```python
success, output = get_cli().execute_lua_script(script, filename)
```
Aseprite opens the file as a CLI arg. `app.activeSprite` is set automatically.

```lua
local spr = app.activeSprite
if not spr then return "No active sprite" end
```

### Pattern 2: Without filename (creating new sprites, multi-file ops)
```python
success, output = get_cli().execute_lua_script(script)
```
Script must open the file itself:

```lua
local spr = app.open("path/to/file.aseprite")
if not spr then return "Error: could not open sprite" end
-- ... work with spr ...
spr:saveAs(spr.filename)
spr:close()
```

## Common Lua Script Templates

### Find a layer by name
```lua
local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{escaped_layer_name}" then
        target = layer
        break
    end
end
if not target then
    return "Layer '" .. "{escaped_layer_name}" .. "' not found"
end
```

### Get or create a cel
```lua
local cel = target:cel(spr.frames[idx])
if not cel and create_flag then
    local img = Image(spr.width, spr.height, spr.colorMode)
    cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
end
if not cel then return end
```

### Iterate all pixels in an image
```lua
local img = cel.image
for y = 0, img.height - 1 do
    for x = 0, img.width - 1 do
        local px_val = img:getPixel(x, y)
        local r = app.pixelColor.rgbaR(px_val)
        local g = app.pixelColor.rgbaG(px_val)
        local b = app.pixelColor.rgbaB(px_val)
        local a = app.pixelColor.rgbaA(px_val)
        -- process pixel
    end
end
```

### Set a pixel with color
```lua
img:putPixel(x, y, Color(r, g, b, 255))
```

### Use Aseprite tools (rectangle, ellipse, paint bucket)
```lua
app.useTool({
    tool="filled_rectangle",  -- or "rectangle", "ellipse", "filled_ellipse", "paint_bucket"
    color=Color(r, g, b, 255),
    points={Point(x1, y1), Point(x2, y2)}
})
```

### Bresenham line drawing (for thick lines)
```lua
local function put_thick(img, x, y, color, size)
    local r = math.max(0, math.floor(size / 2))
    for oy = -r, r do
        for ox = -r, r do
            img:putPixel(x + ox, y + oy, color)
        end
    end
end

local function draw_line(img, x0, y0, x1, y1, color, size)
    local dx = math.abs(x1 - x0)
    local sx = x0 < x1 and 1 or -1
    local dy = -math.abs(y1 - y0)
    local sy = y0 < y1 and 1 or -1
    local err = dx + dy
    while true do
        if size > 1 then
            put_thick(img, x0, y0, color, size)
        else
            img:putPixel(x0, y0, color)
        end
        if x0 == x1 and y0 == y1 then break end
        local e2 = 2 * err
        if e2 >= dy then err = err + dy; x0 = x0 + sx end
        if e2 <= dx then err = err + dx; y0 = y0 + sy end
    end
end
```

### Scanline polygon fill
```lua
local function fill_polygon(img, pts, color)
    local minY = pts[1].y
    local maxY = pts[1].y
    for i = 2, #pts do
        if pts[i].y < minY then minY = pts[i].y end
        if pts[i].y > maxY then maxY = pts[i].y end
    end
    for y = minY, maxY do
        local nodes = {}
        local j = #pts
        for i = 1, #pts do
            local xi, yi = pts[i].x, pts[i].y
            local xj, yj = pts[j].x, pts[j].y
            if (yi < y and yj >= y) or (yj < y and yi >= y) then
                local x = xi + (y - yi) * (xj - xi) / (yj - yi)
                table.insert(nodes, x)
            end
            j = i
        end
        table.sort(nodes)
        for k = 1, #nodes, 2 do
            if nodes[k + 1] ~= nil then
                local x_start = math.floor(nodes[k] + 0.5)
                local x_end = math.floor(nodes[k + 1] + 0.5)
                for x = x_start, x_end do
                    img:putPixel(x, y, color)
                end
            end
        end
    end
end
```

### Easing functions
```lua
local function ease_linear(t) return t end
local function ease_in(t) return t * t * t end
local function ease_out(t) return 1 - (1 - t) ^ 3 end
local function ease_in_out(t)
    if t < 0.5 then return 4 * t * t * t
    else return 1 - ((-2 * t + 2) ^ 3) / 2 end
end
local function smoothstep(t) return t * t * (3 - 2 * t) end
```

### JSON output (legacy pattern)
```lua
print("JSON_START" .. json.encode({result = "value"}))
```

### Key-value output (new pattern)
```lua
print(string.format("PIXEL:%d,%d,%d,%d,%d,%d", x, y, r, g, b, a))
print("ERROR:Layer not found")
```

## Boolean Conversion

Python `True`/`False` → Lua `true`/`false`:
```python
def _lua_bool(val: bool) -> str:
    return "true" if val else "false"
```

## Frame Index Convention

All new tools use **1-based** frame indices (matching Lua convention):
```lua
-- Frame indices are 1-based in Lua
local frame = spr.frames[frame_index]  -- frame_index is 1-based
```

Pixel coordinates are **0-based** (matching Aseprite image API):
```lua
img:getPixel(0, 0)  -- top-left pixel
```