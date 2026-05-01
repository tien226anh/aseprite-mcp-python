"""Canvas creation and management tools for Aseprite MCP."""

from __future__ import annotations

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import _lua_escape, check_file, get_cli


@mcp.tool()
async def create_canvas(
    width: int, height: int, filename: str = "canvas.aseprite"
) -> str:
    """Create a new Aseprite canvas with specified dimensions.

    Args:
        width: Canvas width in pixels (must be > 0)
        height: Canvas height in pixels (must be > 0)
        filename: Path to save the new sprite file (default: canvas.aseprite)
    """
    if width <= 0:
        return f"Error: width must be > 0, got {width}"
    if height <= 0:
        return f"Error: height must be > 0, got {height}"
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"

    escaped_filename = _lua_escape(filename.replace("\\", "/"))

    script = f"""
local spr = Sprite({width}, {height})
spr:saveAs("{escaped_filename}")
return "Created canvas " .. spr.filename
"""

    success, output = get_cli().execute_lua_script(script)
    if success:
        return f"Created canvas: {filename}"
    return f"Failed to create canvas: {output}"


@mcp.tool()
async def add_layer(filename: str, layer_name: str) -> str:
    """Add a new layer to an Aseprite file.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name for the new layer
    """
    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer_name = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

local layer = nil
app.transaction(function()
    layer = spr:newLayer()
    layer.name = "{escaped_layer_name}"
end)

spr:saveAs("{escaped_filename}")
return "Added layer '" .. layer.name .. "' to " .. spr.filename
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Added layer '{layer_name}' to {filename}"
    return f"Failed to add layer: {output}"


@mcp.tool()
async def add_frame(filename: str) -> str:
    """Add a new frame to an Aseprite file.

    Args:
        filename: Path to the Aseprite file
    """
    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

app.transaction(function()
    spr:newFrame()
end)

spr:saveAs("{escaped_filename}")
return "Added frame to " .. spr.filename
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Added new frame to {filename}"
    return f"Failed to add frame: {output}"


@mcp.tool()
async def set_frame(filename: str, frame_index: int) -> str:
    """Set the active frame by index (1-based).

    Args:
        filename: Path to the Aseprite file
        frame_index: 1-based index of the frame to activate (must be >= 1)
    """
    err = check_file(filename)
    if err:
        return err

    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {frame_index} > #spr.frames then
    return "Frame index " .. {frame_index}
        .. " exceeds total frames (" .. #spr.frames .. ")"
end

app.activeFrame = spr.frames[{frame_index}]
return "Set active frame to {frame_index}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set active frame to {frame_index}"
    return f"Failed to set frame: {output}"


@mcp.tool()
async def set_frame_duration(
    filename: str, frame_index: int, duration_ms: int
) -> str:
    """Set the duration of a specific frame.

    Args:
        filename: Path to the Aseprite file
        frame_index: 1-based index of the frame (must be >= 1)
        duration_ms: Duration in milliseconds (must be > 0)
    """
    err = check_file(filename)
    if err:
        return err

    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"
    if duration_ms <= 0:
        return f"Error: duration_ms must be > 0, got {duration_ms}"

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    duration_sec = duration_ms / 1000.0

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {frame_index} > #spr.frames then
    return "Frame index " .. {frame_index}
        .. " exceeds total frames (" .. #spr.frames .. ")"
end

app.transaction(function()
    spr.frames[{frame_index}].duration = {duration_sec}
end)

spr:saveAs("{escaped_filename}")
return "Set frame " .. {frame_index} .. " duration to {duration_ms}ms"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set frame {frame_index} duration to {duration_ms}ms in {filename}"
    return f"Failed to set frame duration: {output}"


@mcp.tool()
async def set_layer(
    filename: str, layer_name: str, create_if_missing: bool = False
) -> str:
    """Set the active layer by name, optionally creating it if missing.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to activate
        create_if_missing: If True, create the layer if it doesn't exist
    """
    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer_name = _lua_escape(layer_name)

    if create_if_missing:
        script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

local found = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{escaped_layer_name}" then
        found = layer
        break
    end
end

app.transaction(function()
    if not found then
        found = spr:newLayer()
        found.name = "{escaped_layer_name}"
    end
end)

app.activeLayer = found
spr:saveAs("{escaped_filename}")
return "Set active layer to '" .. found.name .. "'"
"""
    else:
        script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

local found = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{escaped_layer_name}" then
        found = layer
        break
    end
end

if not found then
    return "Layer '" .. "{escaped_layer_name}" .. "' not found"
end

app.activeLayer = found
spr:saveAs("{escaped_filename}")
return "Set active layer to '" .. found.name .. "'"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set active layer to '{layer_name}' in {filename}"
    return f"Failed to set layer: {output}"
