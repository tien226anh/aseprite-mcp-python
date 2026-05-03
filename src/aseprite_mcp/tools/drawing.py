"""Drawing tools for Aseprite MCP — pixel-level and shape drawing."""

from __future__ import annotations

from typing import Any

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import (
    _lua_escape,
    check_file,
    get_cli,
    validate_hex_color_alpha,
)

# ---------------------------------------------------------------------------
# Cel position offset helper for putPixel-based drawing
# ---------------------------------------------------------------------------

_CEL_OFFSET_PREFIX = """
local ox = cel.position.x
local oy = cel.position.y
"""

# ---------------------------------------------------------------------------
# Simple drawing tools (operate on the active cel)
# ---------------------------------------------------------------------------


@mcp.tool()
async def draw_pixels(
    filename: str, pixels: list[dict[str, Any]], alpha: int = 255
) -> str:
    """Draw pixels on the canvas with specified colors.

    Args:
        filename: Path to the Aseprite file to modify
        pixels: List of pixel data, each containing:
            {"x": int, "y": int, "color": str, "alpha"?: int}
            where color is a hex code like "#FF0000" or "#FF000080",
            and alpha is an optional per-pixel alpha (0-255, overrides tool alpha)
        alpha: Default alpha for all pixels (0-255, default: 255)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    pixel_lines: list[str] = []
    for pixel in pixels:
        x = pixel.get("x", 0)
        y = pixel.get("y", 0)
        rgba = validate_hex_color_alpha(pixel.get("color", "#000000"))
        if rgba is None:
            return f"Invalid color value: {pixel.get('color')}"
        r, g, b, _default_a = rgba
        pixel_alpha = pixel.get("alpha", alpha) if "alpha" in pixel else alpha
        if not (0 <= pixel_alpha <= 255):
            return f"Error: per-pixel alpha must be 0-255, got {pixel_alpha}"
        line = (
            f"        img:putPixel({x} - ox, {y} - oy, "
            f"Color({r}, {g}, {b}, {pixel_alpha}))"
        )
        pixel_lines.append(line)

    pixel_code = "\n".join(pixel_lines)

    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local cel = app.activeCel
    if not cel then
        app.activeLayer = spr.layers[1]
        app.activeFrame = spr.frames[1]
        cel = app.activeCel
        if not cel then return "No active cel and couldn't create one" end
    end
    local img = cel.image
    local ox = cel.position.x
    local oy = cel.position.y

    app.transaction(function()
{pixel_code}
    end)

    spr:saveAs(spr.filename)
    return "Pixels drawn successfully"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Pixels drawn successfully in {filename}"
    return f"Failed to draw pixels: {output}"


@mcp.tool()
async def draw_line(
    filename: str,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: str = "#000000",
    thickness: int = 1,
    alpha: int = 255,
) -> str:
    """Draw a line on the canvas.

    Args:
        filename: Path to the Aseprite file to modify
        x1: Starting x coordinate
        y1: Starting y coordinate
        x2: Ending x coordinate
        y2: Ending y coordinate
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        thickness: Line thickness in pixels (default: 1)
        alpha: Alpha value 0-255 (default: 255)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    # Alpha param always takes priority over hex-embedded alpha
    a = alpha

    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local cel = app.activeCel
    if not cel then
        app.activeLayer = spr.layers[1]
        app.activeFrame = spr.frames[1]
        cel = app.activeCel
        if not cel then return "No active cel and couldn't create one" end
    end
    local img = cel.image
    local ox = cel.position.x
    local oy = cel.position.y

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        draw_line(img, {x1}, {y1}, {x2}, {y2}, color, {thickness}, ox, oy)
    end)

    spr:saveAs(spr.filename)
    return "Line drawn successfully"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Line drawn successfully in {filename}"
    return f"Failed to draw line: {output}"


@mcp.tool()
async def draw_rectangle(
    filename: str,
    x: int,
    y: int,
    width: int,
    height: int,
    color: str = "#000000",
    fill: bool = False,
    alpha: int = 255,
) -> str:
    """Draw a rectangle on the canvas.

    Args:
        filename: Path to the Aseprite file to modify
        x: Top-left x coordinate
        y: Top-left y coordinate
        width: Width of the rectangle
        height: Height of the rectangle
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        fill: Whether to fill the rectangle (default: False)
        alpha: Alpha value 0-255 (default: 255)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha

    tool_name = "filled_rectangle" if fill else "rectangle"

    # useTool uses sprite-global coords, no cel offset needed
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local cel = app.activeCel
    if not cel then
        app.activeLayer = spr.layers[1]
        app.activeFrame = spr.frames[1]
        cel = app.activeCel
        if not cel then return "No active cel and couldn't create one" end
    end

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        app.useTool({{
            tool="{tool_name}",
            color=color,
            points={{Point({x}, {y}), Point({x + width}, {y + height})}}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Rectangle drawn successfully"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Rectangle drawn successfully in {filename}"
    return f"Failed to draw rectangle: {output}"


@mcp.tool()
async def fill_area(
    filename: str, x: int, y: int, color: str = "#000000", alpha: int = 255
) -> str:
    """Fill an area with color using the paint bucket tool.

    Args:
        filename: Path to the Aseprite file to modify
        x: X coordinate to fill from
        y: Y coordinate to fill from
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        alpha: Alpha value 0-255 (default: 255)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha

    # useTool uses sprite-global coords, no cel offset needed
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local cel = app.activeCel
    if not cel then
        app.activeLayer = spr.layers[1]
        app.activeFrame = spr.frames[1]
        cel = app.activeCel
        if not cel then return "No active cel and couldn't create one" end
    end

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        app.useTool({{
            tool="paint_bucket",
            color=color,
            points={{Point({x}, {y})}}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Area filled successfully"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Area filled successfully in {filename}"
    return f"Failed to fill area: {output}"


@mcp.tool()
async def draw_circle(
    filename: str,
    center_x: int,
    center_y: int,
    radius: int,
    color: str = "#000000",
    fill: bool = False,
    alpha: int = 255,
) -> str:
    """Draw a circle on the canvas.

    Args:
        filename: Path to the Aseprite file to modify
        center_x: X coordinate of circle center
        center_y: Y coordinate of circle center
        radius: Radius of the circle in pixels
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        fill: Whether to fill the circle (default: False)
        alpha: Alpha value 0-255 (default: 255)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha

    tool_name = "filled_ellipse" if fill else "ellipse"

    # useTool uses sprite-global coords, no cel offset needed
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local cel = app.activeCel
    if not cel then
        app.activeLayer = spr.layers[1]
        app.activeFrame = spr.frames[1]
        cel = app.activeCel
        if not cel then return "No active cel and couldn't create one" end
    end

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        app.useTool({{
            tool="{tool_name}",
            color=color,
            points={{
                Point({center_x - radius}, {center_y - radius}),
                Point({center_x + radius}, {center_y + radius})
            }}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Circle drawn successfully"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Circle drawn successfully in {filename}"
    return f"Failed to draw circle: {output}"


@mcp.tool()
async def draw_ellipse(
    filename: str,
    center_x: int,
    center_y: int,
    radius_x: int,
    radius_y: int,
    color: str = "#000000",
    fill: bool = False,
    alpha: int = 255,
) -> str:
    """Draw an ellipse with separate X/Y radii.

    Args:
        filename: Path to the Aseprite file to modify
        center_x: X coordinate of ellipse center
        center_y: Y coordinate of ellipse center
        radius_x: Horizontal radius in pixels
        radius_y: Vertical radius in pixels
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        fill: Whether to fill the ellipse (default: False)
        alpha: Alpha value 0-255 (default: 255)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha

    tool_name = "filled_ellipse" if fill else "ellipse"

    # useTool uses sprite-global coords, no cel offset needed
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local cel = app.activeCel
    if not cel then
        app.activeLayer = spr.layers[1]
        app.activeFrame = spr.frames[1]
        cel = app.activeCel
        if not cel then return "No active cel and couldn't create one" end
    end

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        app.useTool({{
            tool="{tool_name}",
            color=color,
            points={{
                Point({center_x - radius_x}, {center_y - radius_y}),
                Point({center_x + radius_x}, {center_y + radius_y})
            }}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Ellipse drawn successfully"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Ellipse drawn successfully in {filename}"
    return f"Failed to draw ellipse: {output}"


@mcp.tool()
async def draw_text(
    filename: str,
    layer_name: str,
    frame_index: int,
    x: int,
    y: int,
    text: str,
    color: str = "#000000",
    alpha: int = 255,
    create_if_missing: bool = True,
) -> str:
    """Render text onto a sprite.

    Args:
        filename: Path to the Aseprite file to modify
        layer_name: Layer name to target
        frame_index: Frame index starting at 1
        x: X coordinate for text position
        y: Y coordinate for text position
        text: Text string to render
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        alpha: Alpha value 0-255 (default: 255)
        create_if_missing: Create cel if it does not exist (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    if not text:
        return "Error: text must not be empty"

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha

    safe_layer_name = _lua_escape(layer_name)
    esc_text = _lua_escape(text)
    create_flag = "true" if create_if_missing else "false"

    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local idx = {frame_index}
    if idx < 1 or idx > #spr.frames then return "Frame index out of range" end

    local target = nil
    for _, layer in ipairs(spr.layers) do
        if layer.name == "{safe_layer_name}" then target = layer break end
    end
    if not target then return "Layer not found" end

    app.activeLayer = target
    app.activeFrame = spr.frames[idx]
    local cel = target:cel(spr.frames[idx])
    if not cel and {create_flag} then
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
    end
    if not cel then return "No cel at layer/frame" end

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        app.useTool({{
            tool="text",
            color=color,
            points={{Point({x}, {y})}},
            text="{esc_text}"
        }})
    end)

    spr:saveAs(spr.filename)
    return "Text drawn successfully"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Text drawn on '{layer_name}' frame {frame_index} in {filename}"
    return f"Failed to draw text: {output}"


# ---------------------------------------------------------------------------
# Layer/frame-targeted drawing tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def draw_pixels_at(
    filename: str,
    layer_name: str,
    frame_index: int,
    pixels: list[dict[str, Any]],
    alpha: int = 255,
    create_if_missing: bool = True,
) -> str:
    """Draw pixels on a specific layer/frame.

    Args:
        filename: Path to the Aseprite file to modify
        layer_name: Layer name to target
        frame_index: Frame index starting at 1
        pixels: List of pixel data with x/y/color, optional per-pixel alpha
        alpha: Default alpha for all pixels (0-255, default: 255)
        create_if_missing: Create cel if it does not exist (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    safe_layer_name = _lua_escape(layer_name)
    create_flag = "true" if create_if_missing else "false"

    pixel_lines: list[str] = []
    for pixel in pixels:
        x = pixel.get("x", 0)
        y = pixel.get("y", 0)
        rgba = validate_hex_color_alpha(pixel.get("color", "#000000"))
        if rgba is None:
            return f"Invalid color value: {pixel.get('color')}"
        r, g, b, _default_a = rgba
        pixel_alpha = pixel.get("alpha", alpha) if "alpha" in pixel else alpha
        if not (0 <= pixel_alpha <= 255):
            return f"Error: per-pixel alpha must be 0-255, got {pixel_alpha}"
        line = (
            f"        img:putPixel({x} - ox, {y} - oy, "
            f"Color({r}, {g}, {b}, {pixel_alpha}))"
        )
        pixel_lines.append(line)

    pixel_code = "\n".join(pixel_lines)

    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local idx = {frame_index}
    if idx < 1 or idx > #spr.frames then return "Frame index out of range" end

    local target = nil
    for _, layer in ipairs(spr.layers) do
        if layer.name == "{safe_layer_name}" then target = layer break end
    end
    if not target then return "Layer not found" end

    app.activeLayer = target
    app.activeFrame = spr.frames[idx]
    local cel = target:cel(spr.frames[idx])
    if not cel and {create_flag} then
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
    end
    if not cel then return "No cel at layer/frame" end
    local img = cel.image
    local ox = cel.position.x
    local oy = cel.position.y

    app.transaction(function()
{pixel_code}
    end)

    spr:saveAs(spr.filename)
    return "Pixels drawn"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Pixels drawn on '{layer_name}' frame {frame_index} in {filename}"
    return f"Failed to draw pixels: {output}"


@mcp.tool()
async def draw_line_at(
    filename: str,
    layer_name: str,
    frame_index: int,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: str = "#000000",
    thickness: int = 1,
    alpha: int = 255,
    create_if_missing: bool = True,
) -> str:
    """Draw a line on a specific layer/frame.

    Args:
        filename: Path to the Aseprite file to modify
        layer_name: Layer name to target
        frame_index: Frame index starting at 1
        x1: Starting x coordinate
        y1: Starting y coordinate
        x2: Ending x coordinate
        y2: Ending y coordinate
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        thickness: Line thickness in pixels (default: 1)
        alpha: Alpha value 0-255 (default: 255)
        create_if_missing: Create cel if it does not exist (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha
    safe_layer_name = _lua_escape(layer_name)
    create_flag = "true" if create_if_missing else "false"

    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local function put_thick(img, x, y, color, size, ox, oy)
        local r = math.max(0, math.floor(size / 2))
        for dy = -r, r do
            for dx = -r, r do
                img:putPixel(x + dx - ox, y + dy - oy, color)
            end
        end
    end

    local function draw_line(img, x0, y0, x1, y1, color, size, ox, oy)
        local dx = math.abs(x1 - x0)
        local sx = x0 < x1 and 1 or -1
        local dy = -math.abs(y1 - y0)
        local sy = y0 < y1 and 1 or -1
        local err = dx + dy
        while true do
            if size > 1 then
                put_thick(img, x0, y0, color, size, ox, oy)
            else
                img:putPixel(x0 - ox, y0 - oy, color)
            end
            if x0 == x1 and y0 == y1 then break end
            local e2 = 2 * err
            if e2 >= dy then err = err + dy; x0 = x0 + sx end
            if e2 <= dx then err = err + dx; y0 = y0 + sy end
        end
    end

    local idx = {frame_index}
    if idx < 1 or idx > #spr.frames then return "Frame index out of range" end

    local target = nil
    for _, layer in ipairs(spr.layers) do
        if layer.name == "{safe_layer_name}" then target = layer break end
    end
    if not target then return "Layer not found" end

    app.activeLayer = target
    app.activeFrame = spr.frames[idx]
    local cel = target:cel(spr.frames[idx])
    if not cel and {create_flag} then
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
    end
    if not cel then return "No cel at layer/frame" end
    local img = cel.image
    local ox = cel.position.x
    local oy = cel.position.y

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        draw_line(img, {x1}, {y1}, {x2}, {y2}, color, {thickness}, ox, oy)
    end)

    spr:saveAs(spr.filename)
    return "Line drawn"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Line drawn on '{layer_name}' frame {frame_index} in {filename}"
    return f"Failed to draw line: {output}"


@mcp.tool()
async def draw_rectangle_at(
    filename: str,
    layer_name: str,
    frame_index: int,
    x: int,
    y: int,
    width: int,
    height: int,
    color: str = "#000000",
    fill: bool = False,
    alpha: int = 255,
    create_if_missing: bool = True,
) -> str:
    """Draw a rectangle on a specific layer/frame.

    Args:
        filename: Path to the Aseprite file to modify
        layer_name: Layer name to target
        frame_index: Frame index starting at 1
        x: Top-left x coordinate
        y: Top-left y coordinate
        width: Width of the rectangle
        height: Height of the rectangle
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        fill: Whether to fill the rectangle (default: False)
        alpha: Alpha value 0-255 (default: 255)
        create_if_missing: Create cel if it does not exist (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha
    safe_layer_name = _lua_escape(layer_name)
    create_flag = "true" if create_if_missing else "false"
    tool_name = "filled_rectangle" if fill else "rectangle"

    # useTool uses sprite-global coords, no cel offset needed
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local idx = {frame_index}
    if idx < 1 or idx > #spr.frames then return "Frame index out of range" end

    local target = nil
    for _, layer in ipairs(spr.layers) do
        if layer.name == "{safe_layer_name}" then target = layer break end
    end
    if not target then return "Layer not found" end

    app.activeLayer = target
    app.activeFrame = spr.frames[idx]
    local cel = target:cel(spr.frames[idx])
    if not cel and {create_flag} then
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
    end
    if not cel then return "No cel at layer/frame" end

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        app.useTool({{
            tool="{tool_name}",
            color=color,
            points={{Point({x}, {y}), Point({x + width}, {y + height})}}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Rectangle drawn"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Rectangle drawn on '{layer_name}' frame {frame_index} in {filename}"
    return f"Failed to draw rectangle: {output}"


@mcp.tool()
async def draw_circle_at(
    filename: str,
    layer_name: str,
    frame_index: int,
    center_x: int,
    center_y: int,
    radius: int,
    color: str = "#000000",
    fill: bool = False,
    alpha: int = 255,
    create_if_missing: bool = True,
) -> str:
    """Draw a circle on a specific layer/frame.

    Args:
        filename: Path to the Aseprite file to modify
        layer_name: Layer name to target
        frame_index: Frame index starting at 1
        center_x: X coordinate of circle center
        center_y: Y coordinate of circle center
        radius: Radius of the circle in pixels
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        fill: Whether to fill the circle (default: False)
        alpha: Alpha value 0-255 (default: 255)
        create_if_missing: Create cel if it does not exist (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha
    safe_layer_name = _lua_escape(layer_name)
    create_flag = "true" if create_if_missing else "false"
    tool_name = "filled_ellipse" if fill else "ellipse"

    # useTool uses sprite-global coords, no cel offset needed
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local idx = {frame_index}
    if idx < 1 or idx > #spr.frames then return "Frame index out of range" end

    local target = nil
    for _, layer in ipairs(spr.layers) do
        if layer.name == "{safe_layer_name}" then target = layer break end
    end
    if not target then return "Layer not found" end

    app.activeLayer = target
    app.activeFrame = spr.frames[idx]
    local cel = target:cel(spr.frames[idx])
    if not cel and {create_flag} then
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
    end
    if not cel then return "No cel at layer/frame" end

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        app.useTool({{
            tool="{tool_name}",
            color=color,
            points={{
                Point({center_x - radius}, {center_y - radius}),
                Point({center_x + radius}, {center_y + radius})
            }}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Circle drawn"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Circle drawn on '{layer_name}' frame {frame_index} in {filename}"
    return f"Failed to draw circle: {output}"


@mcp.tool()
async def fill_area_at(
    filename: str,
    layer_name: str,
    frame_index: int,
    x: int,
    y: int,
    color: str = "#000000",
    alpha: int = 255,
    create_if_missing: bool = True,
) -> str:
    """Fill an area on a specific layer/frame.

    Args:
        filename: Path to the Aseprite file to modify
        layer_name: Layer name to target
        frame_index: Frame index starting at 1
        x: X coordinate to fill from
        y: Y coordinate to fill from
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        alpha: Alpha value 0-255 (default: 255)
        create_if_missing: Create cel if it does not exist (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha
    safe_layer_name = _lua_escape(layer_name)
    create_flag = "true" if create_if_missing else "false"

    # useTool uses sprite-global coords, no cel offset needed
    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local idx = {frame_index}
    if idx < 1 or idx > #spr.frames then return "Frame index out of range" end

    local target = nil
    for _, layer in ipairs(spr.layers) do
        if layer.name == "{safe_layer_name}" then target = layer break end
    end
    if not target then return "Layer not found" end

    app.activeLayer = target
    app.activeFrame = spr.frames[idx]
    local cel = target:cel(spr.frames[idx])
    if not cel and {create_flag} then
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
    end
    if not cel then return "No cel at layer/frame" end

    app.transaction(function()
        local color = Color({r}, {g}, {b}, {a})
        app.useTool({{
            tool="paint_bucket",
            color=color,
            points={{Point({x}, {y})}}
        }})
    end)

    spr:saveAs(spr.filename)
    return "Area filled"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Area filled on '{layer_name}' frame {frame_index} in {filename}"
    return f"Failed to fill area: {output}"


@mcp.tool()
async def draw_polygon(
    filename: str,
    layer_name: str,
    frame_index: int,
    points: list[dict[str, int]],
    color: str = "#000000",
    fill: bool = False,
    alpha: int = 255,
    create_if_missing: bool = True,
) -> str:
    """Draw a polygon on a specific layer/frame.

    Args:
        filename: Path to the Aseprite file to modify
        layer_name: Layer name to target
        frame_index: Frame index starting at 1
        points: List of vertex coordinates, each: {"x": int, "y": int} (min 3)
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        fill: Whether to fill the polygon (default: False)
        alpha: Alpha value 0-255 (default: 255)
        create_if_missing: Create cel if it does not exist (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    if len(points) < 3:
        return "Polygon requires at least 3 points"

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha
    safe_layer_name = _lua_escape(layer_name)
    create_flag = "true" if create_if_missing else "false"
    fill_flag = "true" if fill else "false"
    # Offset point coordinates by cel position for putPixel calls
    points_lua = ", ".join(
        f"{{x={p['x']}, y={p['y']}}}" for p in points
    )

    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local function draw_line(img, x0, y0, x1, y1, color)
        local dx = math.abs(x1 - x0)
        local sx = x0 < x1 and 1 or -1
        local dy = -math.abs(y1 - y0)
        local sy = y0 < y1 and 1 or -1
        local err = dx + dy
        while true do
            img:putPixel(x0, y0, color)
            if x0 == x1 and y0 == y1 then break end
            local e2 = 2 * err
            if e2 >= dy then err = err + dy; x0 = x0 + sx end
            if e2 <= dx then err = err + dx; y0 = y0 + sy end
        end
    end

    local function fill_polygon(img, pts, color)
        local minY = pts[1].y
        local maxY = pts[1].y
        for i = 2, #pts do
            if pts[i].y < minY then minY = pts[i].y end
            if pts[i].y > maxY then maxY = pts[i].y end
        end
        for y = minY, maxY do
            local nodes = {{}}
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

    local idx = {frame_index}
    if idx < 1 or idx > #spr.frames then return "Frame index out of range" end

    local target = nil
    for _, layer in ipairs(spr.layers) do
        if layer.name == "{safe_layer_name}" then target = layer break end
    end
    if not target then return "Layer not found" end

    app.activeLayer = target
    app.activeFrame = spr.frames[idx]
    local cel = target:cel(spr.frames[idx])
    if not cel and {create_flag} then
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
    end
    if not cel then return "No cel at layer/frame" end
    local img = cel.image
    local ox = cel.position.x
    local oy = cel.position.y
    local color = Color({r}, {g}, {b}, {a})
    local pts = {{ {points_lua} }}
    -- Adjust all points to image-local coordinates
    for i = 1, #pts do
        pts[i].x = pts[i].x - ox
        pts[i].y = pts[i].y - oy
    end

    app.transaction(function()
        if {fill_flag} then
            fill_polygon(img, pts, color)
        end
        for i = 1, #pts do
            local n = i + 1
            if n > #pts then n = 1 end
            draw_line(img, pts[i].x, pts[i].y, pts[n].x, pts[n].y, color)
        end
    end)

    spr:saveAs(spr.filename)
    return "Polygon drawn"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Polygon drawn on '{layer_name}' frame {frame_index} in {filename}"
    return f"Failed to draw polygon: {output}"


@mcp.tool()
async def draw_path(
    filename: str,
    layer_name: str,
    frame_index: int,
    points: list[dict[str, int]],
    color: str = "#000000",
    thickness: int = 1,
    alpha: int = 255,
    create_if_missing: bool = True,
) -> str:
    """Draw a path using a polyline on a specific layer/frame.

    Args:
        filename: Path to the Aseprite file to modify
        layer_name: Layer name to target
        frame_index: Frame index starting at 1
        points: List of vertex coordinates, each: {"x": int, "y": int} (min 2)
        color: Hex color code (default: "#000000"), supports #RRGGBBAA
        thickness: Line thickness in pixels (default: 1)
        alpha: Alpha value 0-255 (default: 255)
        create_if_missing: Create cel if it does not exist (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    if len(points) < 2:
        return "Path requires at least 2 points"

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    rgba = validate_hex_color_alpha(color)
    if rgba is None:
        return f"Invalid color value: {color}"
    r, g, b, _default_a = rgba
    a = alpha
    safe_layer_name = _lua_escape(layer_name)
    create_flag = "true" if create_if_missing else "false"
    points_lua = ", ".join(f"{{x={p['x']}, y={p['y']}}}" for p in points)

    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local function put_thick(img, x, y, color, size, ox, oy)
        local r = math.max(0, math.floor(size / 2))
        for dy = -r, r do
            for dx = -r, r do
                img:putPixel(x + dx - ox, y + dy - oy, color)
            end
        end
    end

    local function draw_line(img, x0, y0, x1, y1, color, size, ox, oy)
        local dx = math.abs(x1 - x0)
        local sx = x0 < x1 and 1 or -1
        local dy = -math.abs(y1 - y0)
        local sy = y0 < y1 and 1 or -1
        local err = dx + dy
        while true do
            if size > 1 then
                put_thick(img, x0, y0, color, size, ox, oy)
            else
                img:putPixel(x0 - ox, y0 - oy, color)
            end
            if x0 == x1 and y0 == y1 then break end
            local e2 = 2 * err
            if e2 >= dy then err = err + dy; x0 = x0 + sx end
            if e2 <= dx then err = err + dx; y0 = y0 + sy end
        end
    end

    local idx = {frame_index}
    if idx < 1 or idx > #spr.frames then return "Frame index out of range" end

    local target = nil
    for _, layer in ipairs(spr.layers) do
        if layer.name == "{safe_layer_name}" then target = layer break end
    end
    if not target then return "Layer not found" end

    app.activeLayer = target
    app.activeFrame = spr.frames[idx]
    local cel = target:cel(spr.frames[idx])
    if not cel and {create_flag} then
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
    end
    if not cel then return "No cel at layer/frame" end
    local img = cel.image
    local ox = cel.position.x
    local oy = cel.position.y
    local color = Color({r}, {g}, {b}, {a})
    local pts = {{ {points_lua} }}

    app.transaction(function()
        for i = 1, #pts - 1 do
            draw_line(
                img, pts[i].x, pts[i].y,
                pts[i + 1].x, pts[i + 1].y,
                color, {thickness}, ox, oy
            )
        end
    end)

    spr:saveAs(spr.filename)
    return "Path drawn"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Path drawn on '{layer_name}' frame {frame_index} in {filename}"
    return f"Failed to draw path: {output}"


@mcp.tool()
async def apply_gradient_rect(
    filename: str,
    layer_name: str,
    frame_index: int,
    x: int,
    y: int,
    width: int,
    height: int,
    color_start: str,
    color_end: str,
    alpha: int = 255,
    horizontal: bool = True,
    create_if_missing: bool = True,
) -> str:
    """Apply a linear gradient fill to a rectangle.

    Args:
        filename: Path to the Aseprite file to modify
        layer_name: Layer name to target
        frame_index: Frame index starting at 1
        x: Top-left x coordinate of the rectangle
        y: Top-left y coordinate of the rectangle
        width: Width of the rectangle (must be > 0)
        height: Height of the rectangle (must be > 0)
        color_start: Starting hex color code (e.g. "#FF0000" or "#FF000080")
        color_end: Ending hex color code (e.g. "#0000FF" or "#0000FF80")
        alpha: Alpha value 0-255 (default: 255)
        horizontal: Gradient direction (True = horizontal, False = vertical)
        create_if_missing: Create cel if it does not exist (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    if width <= 0 or height <= 0:
        return "Width and height must be > 0"

    if not (0 <= alpha <= 255):
        return "Error: alpha must be 0-255"

    start_rgba = validate_hex_color_alpha(color_start)
    if start_rgba is None:
        return f"Invalid color_start value: {color_start}"
    end_rgba = validate_hex_color_alpha(color_end)
    if end_rgba is None:
        return f"Invalid color_end value: {color_end}"

    sr, sg, sb, sa = start_rgba
    er, eg, eb, ea = end_rgba
    # Alpha param always takes priority over hex-embedded alpha
    sa = alpha
    ea = alpha
    safe_layer_name = _lua_escape(layer_name)
    create_flag = "true" if create_if_missing else "false"
    horiz_flag = "true" if horizontal else "false"

    script = f"""
    local spr = app.activeSprite
    if not spr then return "No active sprite" end

    local idx = {frame_index}
    if idx < 1 or idx > #spr.frames then return "Frame index out of range" end

    local target = nil
    for _, layer in ipairs(spr.layers) do
        if layer.name == "{safe_layer_name}" then target = layer break end
    end
    if not target then return "Layer not found" end

    app.activeLayer = target
    app.activeFrame = spr.frames[idx]
    local cel = target:cel(spr.frames[idx])
    if not cel and {create_flag} then
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, spr.frames[idx], img, Point(0, 0))
    end
    if not cel then return "No cel at layer/frame" end
    local img = cel.image
    local ox = cel.position.x
    local oy = cel.position.y
    local w = {width}
    local h = {height}

    app.transaction(function()
        for iy = 0, h - 1 do
            for ix = 0, w - 1 do
                local t = 0
                if {horiz_flag} then
                    t = (w > 1) and (ix / (w - 1)) or 0
                else
                    t = (h > 1) and (iy / (h - 1)) or 0
                end
                local r = math.floor({sr} + ({er} - {sr}) * t + 0.5)
                local g = math.floor({sg} + ({eg} - {sg}) * t + 0.5)
                local b = math.floor({sb} + ({eb} - {sb}) * t + 0.5)
                local a = math.floor({sa} + ({ea} - {sa}) * t + 0.5)
                img:putPixel({x} + ix - ox, {y} + iy - oy, Color(r, g, b, a))
            end
        end
    end)

    spr:saveAs(spr.filename)
    return "Gradient applied"
    """

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Gradient applied on '{layer_name}' frame {frame_index} in {filename}"
    return f"Failed to apply gradient: {output}"
