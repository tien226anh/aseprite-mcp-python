# Aseprite Lua API Gotchas

## Common API Misuse Patterns

### 1. `app.activeSprite` vs `app.open()`

**Gotcha**: `app.activeSprite` is nil unless a sprite is already open.

**Correct usage**:
- When `execute_lua_script(script, filename)` is called with a filename, Aseprite opens it as a CLI arg → `app.activeSprite` is set.
- When called without filename, the script must open the sprite itself:
```lua
local spr = app.open("path/to/sprite.aseprite")
if not spr then return "Error: Cannot open sprite" end
```

---

### 2. Layer Access by Name

**Gotcha**: Aseprite doesn't have a built-in `findLayerByName()` function. You must iterate.

**Correct pattern**:
```lua
local function find_layer(spr, name)
    for _, layer in ipairs(spr.layers) do
        if layer.name == name then return layer end
    end
    return nil
end
```

**Note**: Layer names are case-sensitive. `"Outline"` ≠ `"outline"`.

---

### 3. Frame Indexing

**Gotcha**: Frames are 1-based in Lua (`spr.frames[1]` is the first frame).

**Correct usage**:
```lua
-- First frame
local frame1 = spr.frames[1]

-- Last frame
local last = spr.frames[#spr.frames]

-- Iterate all frames
for i = 1, #spr.frames do
    local frame = spr.frames[i]
end
```

---

### 4. Pixel Coordinates

**Gotcha**: Pixel coordinates are 0-based (`img:getPixel(0, 0)` is top-left).

**Correct usage**:
```lua
-- Top-left pixel
local pixel = img:getPixel(0, 0)

-- Bottom-right pixel
local pixel = img:getPixel(img.width - 1, img.height - 1)
```

---

### 5. Color Values

**Gotcha**: `img:getPixel()` returns a packed integer, not a table.

**Correct usage**:
```lua
local pixel = img:getPixel(x, y)
local r = app.pixelColor.rgbaR(pixel)
local g = app.pixelColor.rgbaG(pixel)
local b = app.pixelColor.rgbaB(pixel)
local a = app.pixelColor.rgbaA(pixel)
```

**To create a color value**:
```lua
local color = app.pixelColor.rgba(r, g, b, a)
-- Or for opaque:
local color = app.pixelColor.rgba(r, g, b, 255)
```

---

### 6. `img:drawPixel()` vs `img:clear()`

**Gotcha**: `img:drawPixel()` draws on the image. `img:clear()` clears the entire image.

**Correct usage**:
```lua
-- Draw a single pixel
img:drawPixel(x, y, color)

-- Clear entire image to transparent
img:clear()

-- Clear to a specific color
img:clear(color)
```

---

### 7. `app.useTool()` for Drawing

**Gotcha**: `app.useTool()` is the Aseprite way to use tools (pencil, brush, fill, etc.) but it operates on the active sprite/cel.

**Correct usage**:
```lua
app.useTool{
    tool="pencil",
    color=app.pixelColor.rgba(255, 0, 0, 255),
    points={Point(x1, y1), Point(x2, y2)},
    layer=layer,
    frame=spr.frames[frame_idx]
}
```

**Note**: For batch scripts, direct `img:drawPixel()` is often simpler and more reliable than `app.useTool()`.

---

### 8. `Cel` Creation

**Gotcha**: Creating a new cel requires an Image object.

**Correct usage**:
```lua
local img = Image(spr.width, spr.height)
img:drawPixel(10, 10, app.pixelColor.rgba(255, 0, 0, 255))

local cel = Cel(img)
cel.position = Point(0, 0)
layer:addCel(cel, spr.frames[frame_idx])
```

**Note**: `Cel(Image)` creates a cel with the given image. The cel must be added to a layer and frame.

---

### 9. `app.transaction()` Required for Mutations

**Gotcha**: Most sprite mutations must be wrapped in `app.transaction()`.

**Correct usage**:
```lua
app.transaction(function()
    spr:newFrame()
    spr:newLayer("test")
    -- other mutations
end)
```

**What needs a transaction**:
- Adding/removing frames
- Adding/removing layers
- Adding/removing cels
- Changing cel positions
- Changing layer properties

**What doesn't need a transaction**:
- Reading properties (width, height, etc.)
- `img:drawPixel()` (operates on image data directly)

---

### 10. `spr:saveAs()` Path

**Gotcha**: `saveAs` requires forward slashes on all platforms.

**Correct usage**:
```lua
spr:saveAs("C:/Users/name/sprite.aseprite")  -- not "C:\Users\name\..."
```

---

### 11. `Image` Constructor

**Gotcha**: `Image(width, height)` creates a new transparent image. `Image(imgSpec)` creates from a specification.

**Correct usage**:
```lua
-- New transparent image
local img = Image(32, 32)

-- From sprite specification
local img = Image(spr.spec)

-- Copy existing image
local img = Image(existingImg)
```

---

### 12. `app.command` Functions

**Gotcha**: `app.command.*` functions are Aseprite menu commands. They operate on the active sprite.

**Common commands**:
```lua
app.command.FlattenLayers()
app.command.CanvasSize{ width=64, height=64 }
app.command.SpriteSize{ scale=2 }
app.command.Rotate{ angle=90 }
app.command.Flip{ horizontal=true }
```

**Note**: These are less reliable in batch mode than direct API calls. Prefer direct API when possible.

---

### 13. `Tag` Creation

**Gotcha**: Tags are created on the sprite, not on individual frames.

**Correct usage**:
```lua
local tag = Tag(spr.frames[1])
tag.fromFrame = spr.frames[1]
tag.toFrame = spr.frames[4]
tag.name = "idle"
tag.color = app.pixelColor.rgba(255, 0, 0, 255)  -- tag color (optional)
spr.tags:add(tag)
```

---

### 14. Palette Access

**Gotcha**: `spr.palettes[1]` is the first palette (1-based). Palette entries are also 1-based.

**Correct usage**:
```lua
local pal = spr.palettes[1]
for i = 1, #pal do
    local color = pal:getColor(i)
    print(i, color.red, color.green, color.blue, color.alpha)
end
```

---

### 15. `Point` and `Rectangle` Types

**Gotcha**: Aseprite uses `Point` and `Rectangle` types, not plain tables.

**Correct usage**:
```lua
-- Point
local pt = Point(10, 20)
print(pt.x, pt.y)  -- 10, 20

-- Rectangle
local rect = Rectangle(0, 0, 32, 32)
print(rect.x, rect.y, rect.width, rect.height)  -- 0, 0, 32, 32

-- Cel position is a Point
cel.position = Point(5, 10)
```

---

### 16. `app.pixelColor` Functions

**Gotcha**: These are utility functions for color manipulation, not methods.

**Correct usage**:
```lua
-- Create RGBA color
local color = app.pixelColor.rgba(255, 128, 0, 255)

-- Extract components
local r = app.pixelColor.rgbaR(color)  -- 255
local g = app.pixelColor.rgbaG(color)  -- 128
local b = app.pixelColor.rgbaB(color)  -- 0
local a = app.pixelColor.rgbaA(color)  -- 255

-- Create grayscale
local gray = app.pixelColor.graya(128, 255)
```

---

### 17. Layer Types

**Gotcha**: Not all layers are the same. Image layers, group layers, and tilemap layers have different properties.

**Correct usage**:
```lua
for _, layer in ipairs(spr.layers) do
    if layer.isImage then
        -- Image layer (can have cels with images)
    elseif layer.isGroup then
        -- Group layer (contains child layers)
    elseif layer.isTilemap then
        -- Tilemap layer (Aseprite 1.3+)
    end
end
```

---

### 18. `app.params` for Script Parameters

**Gotcha**: When running scripts via CLI with `--script-param`, parameters are in `app.params`.

**Correct usage**:
```bash
aseprite -b --script script.lua --script-param key=value
```

```lua
local value = app.params.key  -- "value"
```

**Note**: The MCP server doesn't use `--script-param`. It generates Lua scripts with embedded values instead.