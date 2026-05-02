# Aseprite Lua API Quick Reference

## Core Objects

### Sprite
```lua
local spr = app.activeSprite          -- Get active sprite
local spr = app.open("path/file.ase") -- Open a file
Sprite(width, height)                  -- Create new sprite (RGB)
Sprite(width, height, ColorMode.INDEXED) -- Create indexed sprite

spr.width, spr.height                 -- Dimensions
spr.colorMode                          -- ColorMode enum
spr.filename                           -- File path
spr.frames                             -- Array of Frame (1-based)
spr.layers                             -- Array of Layer (1-based via ipairs)
spr.tags                               -- Array of Tag
spr.palettes                           -- Array of Palette
spr.bounds                             -- Rectangle of sprite bounds

spr:newEmptyFrame()                    -- Add a new empty frame
spr:newLayer()                         -- Add a new layer
spr:newCel(layer, frame)               -- Create empty cel
spr:newCel(layer, frame, image, pos)   -- Create cel with image
spr:newTag(fromFrame, toFrame)         -- Create a tag
spr:deleteCel(cel)                     -- Delete a cel
spr:saveAs("path.ase")                -- Save sprite
spr:close()                            -- Close sprite

-- Resize/crop (scales all content)
spr:resize(newWidth, newHeight)
spr:crop(x, y, width, height)
```

### Layer
```lua
layer.name                             -- Layer name (string)
layer.visible                          -- Visibility (bool)
layer.opacity                           -- Opacity 0-255 (int)
layer:cel(frame)                       -- Get cel for a frame (may be nil)
```

### Frame
```lua
frame.duration                          -- Duration in seconds (float)
frame.frameNumber                      -- 1-based frame number
```

### Cel
```lua
cel.image                              -- Image object
cel.position                           -- Point(x, y)
cel.opacity                            -- Cel opacity 0-255

cel.position = Point(newX, newY)      -- Set cel position
cel.opacity = 128                       -- Set cel opacity
```

### Image
```lua
img.width, img.height                  -- Dimensions
img.colorMode                          -- ColorMode enum

img:getPixel(x, y)                     -- Get RGBA pixel value (0-based coords)
img:putPixel(x, y, Color(r,g,b,a))    -- Set pixel directly (no blending)
img:drawPixel(x, y, Color(r,g,b,a))   -- Set pixel with alpha blending

-- Create a new image
local newImg = Image(width, height, colorMode)
local copyImg = Image(existingImg)      -- Copy an image
```

### Color
```lua
Color(r, g, b, a)                      -- Create color (0-255 each)
app.pixelColor.rgbaR(pixelValue)       -- Extract red channel
app.pixelColor.rgbaG(pixelValue)       -- Extract green channel
app.pixelColor.rgbaB(pixelValue)       -- Extract blue channel
app.pixelColor.rgbaA(pixelValue)       -- Extract alpha channel
```

### Palette
```lua
local pal = spr.palettes[1]            -- First palette
#pal                                    -- Number of colors (1-based length)
pal:getColor(index)                    -- Get Color at 0-based index
pal:setColor(index, Color(r,g,b,a))    -- Set color at 0-based index

-- Create new palette
local pal = Palette(numColors)
pal:setColor(0, Color(255, 0, 0, 255)) -- Set first color
spr:setPalette(pal)                     -- Apply palette
```

### Tag
```lua
tag.name                               -- Tag name
tag.fromFrame                          -- Starting Frame object
tag.toFrame                            -- Ending Frame object
tag.aniDir                             -- AniDir.FORWARD/REVERSE/PINGPONG

-- Create/update tag
local tag = spr:newTag(spr.frames[1], spr.frames[4])
tag.name = "idle"
tag.aniDir = AniDir.PINGPONG
```

### Point
```lua
Point(x, y)                            -- Create point
point.x, point.y                       -- Access coordinates
```

### Tools (useTool)
```lua
app.useTool({
    tool = "filled_rectangle",         -- Tool name
    color = Color(r, g, b, 255),       -- Color
    points = {Point(x1, y1), Point(x2, y2)}  -- Points
})
```

Available tool names: `rectangle`, `filled_rectangle`, `ellipse`, `filled_ellipse`, `paint_bucket`, `line`, `pencil`, `eraser`

### Transaction
```lua
app.transaction(function()
    -- All mutations here are grouped as one undo step
    cel.position = Point(10, 20)
    cel.opacity = 200
end)
```

## ColorMode Enum
```lua
ColorMode.RGB        -- 0
ColorMode.GRAYSCALE  -- 1
ColorMode.INDEXED    -- 2
```

## AniDir Enum
```lua
AniDir.FORWARD    -- 0
AniDir.REVERSE    -- 1
AniDir.PINGPONG   -- 2
```

## Important Notes

- **Lua 5.3+**: Use `table.unpack`, NOT `unpack`
- **1-based indexing**: `spr.frames[1]` is first frame, `ipairs()` starts at 1
- **0-based pixels**: `img:getPixel(0, 0)` is top-left
- **`spr:saveAs()`** must use forward slashes in paths
- **`app.transaction()`** groups mutations for undo
- **`img:putPixel`** sets directly, **`img:drawPixel`** blends with alpha