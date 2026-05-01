"""Transform tools for Aseprite MCP — flip, rotate, resize, and crop."""

from __future__ import annotations

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import _lua_escape, check_file, get_cli


@mcp.tool()
async def flip_layer(
    filename: str, layer_name: str, frame_index: int, direction: str = "horizontal"
) -> str:
    """Flip the pixels of a layer's cel horizontally or vertically.

    Args:
        filename: Path to the Aseprite file.
        layer_name: Name of the layer to flip.
        frame_index: 1-based frame index of the cel to flip.
        direction: "horizontal" or "vertical" (default "horizontal").
    """
    err = check_file(filename)
    if err:
        return err

    if direction not in ("horizontal", "vertical"):
        return f'Error: direction must be "horizontal" or "vertical", got "{direction}"'

    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"

    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer = _lua_escape(layer_name)

    # Flip logic: read all pixels into 2D table, then write back with swapped indices
    if direction == "horizontal":
        flip_logic = """local pixels = {}
local w = img.width
local h = img.height
for y = 0, h - 1 do
    pixels[y] = {}
    for x = 0, w - 1 do
        pixels[y][x] = img:getPixel(x, y)
    end
end
-- Write back mirrored horizontally: pixel at (x, y) comes from (w-1-x, y)
for y = 0, h - 1 do
    for x = 0, w - 1 do
        img:drawPixel(x, y, pixels[y][w - 1 - x])
    end
end"""
    else:  # vertical
        flip_logic = """local pixels = {}
local w = img.width
local h = img.height
for y = 0, h - 1 do
    pixels[y] = {}
    for x = 0, w - 1 do
        pixels[y][x] = img:getPixel(x, y)
    end
end
-- Write back mirrored vertically: pixel at (x, y) comes from (x, h-1-y)
for y = 0, h - 1 do
    for x = 0, w - 1 do
        img:drawPixel(x, y, pixels[h - 1 - y][x])
    end
end"""

    script = f"""
local spr = app.open("{escaped_filename}")
if not spr then return "Error: could not open sprite" end

-- Find layer by name
local layer = nil
for _, lyr in ipairs(spr.layers) do
    if lyr.name == "{escaped_layer}" then
        layer = lyr
        break
    end
end
if not layer then
    spr:close()
    return "Error: layer '" .. "{escaped_layer}" .. "' not found"
end

-- Get cel at frame_index (1-based)
if {frame_index} > #spr.frames then
    spr:close()
    return "Error: frame index " .. {frame_index}
        .. " exceeds total frames (" .. #spr.frames .. ")"
end

local cel = layer:cel({frame_index})
if not cel then
    spr:close()
    return "Error: no cel at frame " .. {frame_index}
        .. " on layer '" .. "{escaped_layer}" .. "'"
end

local img = cel.image

app.transaction(function()
    {flip_logic}
end)

spr:saveAs(spr.filename)
spr:close()

return "Flipped layer '"
    .. "{escaped_layer}" .. "' {direction}ly in frame {frame_index}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return (
            f"Flipped layer '{layer_name}' {direction}ly "
            f"in frame {frame_index} of {filename}"
        )
    return f"Failed to flip layer: {output}"


@mcp.tool()
async def rotate_layer(
    filename: str, layer_name: str, frame_index: int, angle: int = 90
) -> str:
    """Rotate a layer's cel by 90°, 180°, or 270° clockwise.

    Args:
        filename: Path to the Aseprite file.
        layer_name: Name of the layer to rotate.
        frame_index: 1-based frame index of the cel to rotate.
        angle: Rotation angle in degrees — must be 90, 180, or 270 (default 90).
    """
    err = check_file(filename)
    if err:
        return err

    if angle not in (90, 180, 270):
        return f"Error: angle must be 90, 180, or 270, got {angle}"

    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"

    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer = _lua_escape(layer_name)

    # Build rotation-specific Lua logic
    if angle == 180:
        rotate_logic = """local pixels = {}
local w = img.width
local h = img.height
for y = 0, h - 1 do
    pixels[y] = {}
    for x = 0, w - 1 do
        pixels[y][x] = img:getPixel(x, y)
    end
end
-- 180° rotation: pixel at (x, y) comes from (w-1-x, h-1-y)
for y = 0, h - 1 do
    for x = 0, w - 1 do
        img:drawPixel(x, y, pixels[h - 1 - y][w - 1 - x])
    end
end"""

        set_cel_image = ""  # No dimension change for 180°
    else:
        # 90° or 270° — dimensions swap, so we need a new Image
        if angle == 90:
            # 90°CW: new_img[x][h-1-y] = old_img[y][x]  →  (new_x, new_y) = (h-1-y, x)
            rotate_logic = """local pixels = {}
local w = img.width
local h = img.height
for y = 0, h - 1 do
    pixels[y] = {}
    for x = 0, w - 1 do
        pixels[y][x] = img:getPixel(x, y)
    end
end
-- Create new image with swapped dimensions for 90° CW rotation
local new_img = Image(h, w, img.colorMode)
for y = 0, h - 1 do
    for x = 0, w - 1 do
        -- 90° CW: source (x, y) → dest (h-1-y, x)
        new_img:drawPixel(h - 1 - y, x, pixels[y][x])
    end
end"""

        else:  # 270
            # 270degCW (= 90degCCW): new_img[y][w-1-x] = old_img[x][y]
            # -> (new_x, new_y) = (y, w-1-x)
            rotate_logic = """local pixels = {}
local w = img.width
local h = img.height
for y = 0, h - 1 do
    pixels[y] = {}
    for x = 0, w - 1 do
        pixels[y][x] = img:getPixel(x, y)
    end
end
-- Create new image with swapped dimensions for 270° CW rotation
local new_img = Image(h, w, img.colorMode)
for y = 0, h - 1 do
    for x = 0, w - 1 do
        -- 270° CW: source (x, y) → dest (y, w-1-x)
        new_img:drawPixel(y, w - 1 - x, pixels[y][x])
    end
end"""

        # For 90° and 270°, we need to replace the cel's image
        set_cel_image = """cel.image = new_img"""

    script = f"""
local spr = app.open("{escaped_filename}")
if not spr then return "Error: could not open sprite" end

-- Find layer by name
local layer = nil
for _, lyr in ipairs(spr.layers) do
    if lyr.name == "{escaped_layer}" then
        layer = lyr
        break
    end
end
if not layer then
    spr:close()
    return "Error: layer '" .. "{escaped_layer}" .. "' not found"
end

-- Get cel at frame_index (1-based)
if {frame_index} > #spr.frames then
    spr:close()
    return "Error: frame index " .. {frame_index}
        .. " exceeds total frames (" .. #spr.frames .. ")"
end

local cel = layer:cel({frame_index})
if not cel then
    spr:close()
    return "Error: no cel at frame " .. {frame_index}
        .. " on layer '" .. "{escaped_layer}" .. "'"
end

local img = cel.image

app.transaction(function()
    {rotate_logic}
    {set_cel_image}
end)

spr:saveAs(spr.filename)
spr:close()

return "Rotated layer '"
    .. "{escaped_layer}" .. "' by {angle} degrees in frame {frame_index}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return (
            f"Rotated layer '{layer_name}' by "
            f"{angle}\u00b0 in frame {frame_index} of {filename}"
        )
    return f"Failed to rotate layer: {output}"


@mcp.tool()
async def resize_canvas(filename: str, width: int, height: int) -> str:
    """Resize a sprite (scales all content, not just the canvas).

    Args:
        filename: Path to the Aseprite file.
        width: New width in pixels (must be > 0).
        height: New height in pixels (must be > 0).
    """
    err = check_file(filename)
    if err:
        return err

    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"

    if width <= 0:
        return f"Error: width must be > 0, got {width}"
    if height <= 0:
        return f"Error: height must be > 0, got {height}"

    escaped_filename = _lua_escape(filename.replace("\\", "/"))

    script = f"""
local spr = app.open("{escaped_filename}")
if not spr then return "Error: could not open sprite" end

app.transaction(function()
    spr:resize({width}, {height})
end)

spr:saveAs(spr.filename)
spr:close()

return "Resized sprite to {width}x{height}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Resized {filename} to {width}x{height}"
    return f"Failed to resize: {output}"


@mcp.tool()
async def crop_canvas(filename: str, x: int, y: int, width: int, height: int) -> str:
    """Crop a sprite to the specified region.

    Args:
        filename: Path to the Aseprite file.
        x: X offset of the crop rectangle.
        y: Y offset of the crop rectangle.
        width: Width of the crop region (must be > 0).
        height: Height of the crop region (must be > 0).
    """
    err = check_file(filename)
    if err:
        return err

    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"

    if width <= 0:
        return f"Error: width must be > 0, got {width}"
    if height <= 0:
        return f"Error: height must be > 0, got {height}"

    escaped_filename = _lua_escape(filename.replace("\\", "/"))

    script = f"""
local spr = app.open("{escaped_filename}")
if not spr then return "Error: could not open sprite" end

app.transaction(function()
    spr:crop({x}, {y}, {width}, {height})
end)

spr:saveAs(spr.filename)
spr:close()

return "Cropped sprite to region ({x}, {y}, {width}, {height})"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Cropped {filename} to region ({x}, {y}, {width}, {height})"
    return f"Failed to crop: {output}"
