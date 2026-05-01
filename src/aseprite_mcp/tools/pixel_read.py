"""Pixel read tools for Aseprite MCP — reading pixel data from sprites."""

from __future__ import annotations

import json

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import _lua_escape, check_file, get_cli


@mcp.tool()
async def get_pixel_color(
    filename: str,
    x: int,
    y: int,
    layer_name: str = "",
    frame_index: int = 1,
) -> str:
    """Read the color of a single pixel from a sprite.

    Args:
        filename: Path to the Aseprite file
        x: X coordinate of the pixel (0-based)
        y: Y coordinate of the pixel (0-based)
        layer_name: Name of the layer to read from. If empty, uses active layer.
        frame_index: 1-based frame index. Default: 1
    """
    err = check_file(filename)
    if err:
        return err

    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"

    safe_layer = _lua_escape(layer_name) if layer_name else ""

    # Build layer lookup code
    if layer_name:
        layer_code = f"""
local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{safe_layer}" then target = layer break end
end
if not target then print("ERROR:Layer not found") return end
local cel = target:cel(spr.frames[frameIdx])"""
    else:
        layer_code = """
app.activeFrame = spr.frames[frameIdx]
local cel = app.activeCel"""

    script = f"""
local spr = app.activeSprite
if not spr then print("ERROR:No active sprite") return end

local frameIdx = {frame_index}
if frameIdx < 1 or frameIdx > #spr.frames then
    print("ERROR:Frame index out of range") return end
{layer_code}
if not cel then print("ERROR:No cel at that layer/frame") return end

local img = cel.image
local px_val = img:getPixel({x}, {y})
local r = app.pixelColor.rgbaR(px_val)
local g = app.pixelColor.rgbaG(px_val)
local b = app.pixelColor.rgbaB(px_val)
local a = app.pixelColor.rgbaA(px_val)
print(string.format("PIXEL:%d,%d,%d,%d", r, g, b, a))
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if not success:
        return f"Failed to read pixel: {output}"

    # Parse PIXEL:r,g,b,a from output
    for line in output.strip().splitlines():
        line = line.strip()
        if line.startswith("ERROR:"):
            return f"Error: {line[6:]}"
        if line.startswith("PIXEL:"):
            parts = line[6:].split(",")
            if len(parts) == 4:
                try:
                    r_val, g_val, b_val, a_val = (
                        int(parts[0]),
                        int(parts[1]),
                        int(parts[2]),
                        int(parts[3]),
                    )
                    hex_str = f"#{r_val:02x}{g_val:02x}{b_val:02x}"
                    return (
                        f"{hex_str} (r={r_val}, g={g_val}, b={b_val}, a={a_val})"
                    )
                except (ValueError, IndexError):
                    pass
            return f"Pixel at ({x}, {y}): {line[6:]}"

    return f"Failed to parse pixel data from output: {output}"


@mcp.tool()
async def get_pixels_rect(
    filename: str,
    x: int,
    y: int,
    width: int,
    height: int,
    layer_name: str = "",
    frame_index: int = 1,
) -> str:
    """Read pixel colors from a rectangular region of a sprite.

    Args:
        filename: Path to the Aseprite file
        x: X coordinate of the rectangle top-left (0-based)
        y: Y coordinate of the rectangle top-left (0-based)
        width: Width of the rectangle in pixels (must be > 0)
        height: Height of the rectangle in pixels (must be > 0)
        layer_name: Name of the layer to read from. If empty, uses active layer.
        frame_index: 1-based frame index. Default: 1
    """
    err = check_file(filename)
    if err:
        return err

    if width <= 0:
        return f"Error: width must be > 0, got {width}"
    if height <= 0:
        return f"Error: height must be > 0, got {height}"
    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"

    safe_layer = _lua_escape(layer_name) if layer_name else ""
    x_end = x + width - 1
    y_end = y + height - 1

    # Build layer lookup code
    if layer_name:
        layer_code = f"""
local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{safe_layer}" then target = layer break end
end
if not target then print("ERROR:Layer not found") return end
local cel = target:cel(spr.frames[frameIdx])"""
    else:
        layer_code = """
app.activeFrame = spr.frames[frameIdx]
local cel = app.activeCel"""

    script = f"""
local spr = app.activeSprite
if not spr then print("ERROR:No active sprite") return end

local frameIdx = {frame_index}
if frameIdx < 1 or frameIdx > #spr.frames then
    print("ERROR:Frame index out of range") return end
{layer_code}
if not cel then print("ERROR:No cel at that layer/frame") return end

local img = cel.image
for py = {y}, {y_end} do
    for px = {x}, {x_end} do
        if px >= 0 and px < img.width and py >= 0 and py < img.height then
            local px_val = img:getPixel(px, py)
            local r = app.pixelColor.rgbaR(px_val)
            local g = app.pixelColor.rgbaG(px_val)
            local b = app.pixelColor.rgbaB(px_val)
            local a = app.pixelColor.rgbaA(px_val)
            print(string.format("PIXEL:%d,%d,%d,%d,%d,%d", px, py, r, g, b, a))
        end
    end
end
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if not success:
        return f"Failed to read pixels: {output}"

    # Parse pixel data from output
    pixels = []
    for line in output.strip().splitlines():
        line = line.strip()
        if line.startswith("ERROR:"):
            return f"Error: {line[6:]}"
        if line.startswith("PIXEL:"):
            parts = line[6:].split(",")
            if len(parts) == 6:
                try:
                    px_x, px_y = int(parts[0]), int(parts[1])
                    r_val, g_val, b_val, a_val = (
                        int(parts[2]),
                        int(parts[3]),
                        int(parts[4]),
                        int(parts[5]),
                    )
                    hex_str = f"#{r_val:02x}{g_val:02x}{b_val:02x}"
                    pixels.append({
                        "x": px_x,
                        "y": px_y,
                        "hex": hex_str,
                        "r": r_val,
                        "g": g_val,
                        "b": b_val,
                        "a": a_val,
                    })
                except (ValueError, IndexError):
                    continue

    return json.dumps({"pixels": pixels, "count": len(pixels)})
