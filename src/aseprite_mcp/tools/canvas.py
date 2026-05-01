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


@mcp.tool()
async def delete_layer(filename: str, layer_name: str) -> str:
    """Delete a layer by name from an Aseprite file.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to delete
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"
    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer_name = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if #spr.layers < 2 then
    return "Error: cannot delete the only layer"
end

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

app.transaction(function()
    spr:deleteLayer(target)
end)

spr:saveAs("{escaped_filename}")
return "Deleted layer '" .. "{escaped_layer_name}" .. "'"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Deleted layer '{layer_name}' from {filename}"
    return f"Failed to delete layer: {output}"


@mcp.tool()
async def rename_layer(
    filename: str, layer_name: str, new_name: str
) -> str:
    """Rename a layer in an Aseprite file.

    Args:
        filename: Path to the Aseprite file
        layer_name: Current name of the layer
        new_name: New name for the layer
    """
    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer_name = _lua_escape(layer_name)
    escaped_new_name = _lua_escape(new_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

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

app.transaction(function()
    target.name = "{escaped_new_name}"
end)

spr:saveAs("{escaped_filename}")
return "Renamed layer '" .. "{escaped_layer_name}" .. "' to '{escaped_new_name}'"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Renamed layer '{layer_name}' to '{new_name}' in {filename}"
    return f"Failed to rename layer: {output}"


@mcp.tool()
async def reorder_layer(
    filename: str, layer_name: str, position: int
) -> str:
    """Move a layer to a specific position in the stack (1-based, 1=bottom).

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to move
        position: Target stack position (1-based, 1=bottom, must be >= 1)
    """
    if position < 1:
        return f"Error: position must be >= 1, got {position}"
    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer_name = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

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

if {position} > #spr.layers then
    return "Position " .. {position} .. " exceeds total layers (" .. #spr.layers .. ")"
end

app.transaction(function()
    target.stackIndex = {position}
end)

spr:saveAs("{escaped_filename}")
return "Moved layer '" .. target.name .. "' to position {position}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Moved layer '{layer_name}' to position {position} in {filename}"
    return f"Failed to reorder layer: {output}"


@mcp.tool()
async def duplicate_layer(
    filename: str, layer_name: str, new_layer_name: str
) -> str:
    """Duplicate a layer with all its cels.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the source layer to duplicate
        new_layer_name: Name for the new duplicated layer
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"
    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer_name = _lua_escape(layer_name)
    escaped_new_name = _lua_escape(new_layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

local srcLayer = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{escaped_layer_name}" then
        srcLayer = layer
        break
    end
end

if not srcLayer then
    return "Layer '" .. "{escaped_layer_name}" .. "' not found"
end

app.transaction(function()
    local newLayer = spr:newLayer()
    newLayer.name = "{escaped_new_name}"
    newLayer.opacity = srcLayer.opacity
    newLayer.blendMode = srcLayer.blendMode
    for i, frame in ipairs(spr.frames) do
        local srcCel = srcLayer:cel(frame)
        if srcCel then
            local newImg = Image(srcCel.image)
            spr:newCel(newLayer, frame, newImg, srcCel.position)
        end
    end
end)

spr:saveAs("{escaped_filename}")
return "Duplicated layer '" .. "{escaped_layer_name}" .. "' as '{escaped_new_name}'"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Duplicated layer '{layer_name}' as '{new_layer_name}' in {filename}"
    return f"Failed to duplicate layer: {output}"


@mcp.tool()
async def merge_layer_down(filename: str, layer_name: str) -> str:
    """Merge a layer with the layer below it.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to merge down
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"
    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer_name = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

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

-- Check if there is a layer below (stackIndex - 1)
if target.stackIndex <= 1 then
    return "Error: no layer below '" .. target.name .. "' to merge with"
end

app.activeLayer = target
app.command.MergeDownLayer()

spr:saveAs("{escaped_filename}")
return "Merged layer '" .. "{escaped_layer_name}" .. "' down"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Merged layer '{layer_name}' down in {filename}"
    return f"Failed to merge layer down: {output}"


@mcp.tool()
async def set_layer_blend_mode(
    filename: str, layer_name: str, blend_mode: str = "normal"
) -> str:
    """Set a layer's blend mode.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to modify
        blend_mode: Blend mode - one of: normal, multiply, screen, overlay,
            darken, lighten, color_dodge, color_burn, hard_light, soft_light,
            difference, exclusion, hue, saturation, color, luminosity, add,
            subtract, divide (default: "normal")
    """
    valid_modes = {
        "normal",
        "multiply",
        "screen",
        "overlay",
        "darken",
        "lighten",
        "color_dodge",
        "color_burn",
        "hard_light",
        "soft_light",
        "difference",
        "exclusion",
        "hue",
        "saturation",
        "color",
        "luminosity",
        "add",
        "subtract",
        "divide",
    }
    if blend_mode not in valid_modes:
        return (
            f"Error: blend_mode must be one of {sorted(valid_modes)}, "
            f"got '{blend_mode}'"
        )
    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    escaped_layer_name = _lua_escape(layer_name)
    mode_upper = blend_mode.upper()

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

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

app.transaction(function()
    target.blendMode = BlendMode.{mode_upper}
end)

spr:saveAs("{escaped_filename}")
return "Set layer '" .. target.name .. "' blend mode to '{blend_mode}'"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set layer '{layer_name}' blend mode to {blend_mode} in {filename}"
    return f"Failed to set blend mode: {output}"
