"""Animation tools for Aseprite MCP — frames, tags, layers, cels, and tweening."""

from __future__ import annotations

import os

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import get_cli, check_file, _lua_escape


# ── Helpers ─────────────────────────────────────────────────────────────────


def _esc_path(filename: str) -> str:
    """Escape a filename for embedding in a Lua string literal, normalizing backslashes."""
    return _lua_escape(filename.replace("\\", "/"))


def _lua_bool(val: bool) -> str:
    """Convert a Python bool to a Lua boolean literal."""
    return "true" if val else "false"


# ── Frame tools ─────────────────────────────────────────────────────────────


@mcp.tool()
async def add_frames(
    filename: str, count: int, duration_ms: int | None = None
) -> str:
    """Add multiple frames to an Aseprite sprite.

    Args:
        filename: Path to the Aseprite file
        count: Number of frames to add (must be >= 1)
        duration_ms: Optional duration in milliseconds for each new frame
    """
    if count < 1:
        return f"Error: count must be >= 1, got {count}"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    if duration_ms is not None:
        dur = duration_ms / 1000.0
        script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

app.transaction(function()
    for i = 1, {count} do
        local f = spr:newEmptyFrame()
        f.duration = {dur}
    end
end)

spr:saveAs("{esc}")
return "Added {count} frames with {duration_ms}ms duration"
"""
    else:
        script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

app.transaction(function()
    for i = 1, {count} do
        spr:newEmptyFrame()
    end
end)

spr:saveAs("{esc}")
return "Added {count} frames"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        msg = f"Added {count} frames to {filename}"
        if duration_ms is not None:
            msg += f" (duration: {duration_ms}ms each)"
        return msg
    return f"Failed to add frames: {output}"


@mcp.tool()
async def set_frame_duration_all(filename: str, duration_ms: int) -> str:
    """Set the duration of all frames in a sprite.

    Args:
        filename: Path to the Aseprite file
        duration_ms: Duration in milliseconds for every frame (must be > 0)
    """
    if duration_ms <= 0:
        return f"Error: duration_ms must be > 0, got {duration_ms}"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    dur = duration_ms / 1000.0

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

app.transaction(function()
    for _, frame in ipairs(spr.frames) do
        frame.duration = {dur}
    end
end)

spr:saveAs("{esc}")
return "Set all frame durations to {duration_ms}ms"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set all frame durations to {duration_ms}ms in {filename}"
    return f"Failed to set frame durations: {output}"


# ── Layer tools ─────────────────────────────────────────────────────────────


@mcp.tool()
async def set_layer_visibility(
    filename: str, layer_name: str, visible: bool = True
) -> str:
    """Set layer visibility by name.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to modify
        visible: Whether the layer should be visible (default: True)
    """
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)
    vis = _lua_bool(visible)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

app.transaction(function()
    target.visible = {vis}
end)

spr:saveAs("{esc}")
return "Set layer '" .. target.name .. "' visibility to {vis}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set layer '{layer_name}' visibility to {visible} in {filename}"
    return f"Failed to set layer visibility: {output}"


@mcp.tool()
async def set_layer_opacity(
    filename: str, layer_name: str, opacity: int
) -> str:
    """Set layer opacity by name.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to modify
        opacity: Opacity value 0-255 (0=invisible, 255=fully opaque)
    """
    if not (0 <= opacity <= 255):
        return f"Error: opacity must be 0-255, got {opacity}"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

app.transaction(function()
    target.opacity = {opacity}
end)

spr:saveAs("{esc}")
return "Set layer '" .. target.name .. "' opacity to {opacity}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set layer '{layer_name}' opacity to {opacity} in {filename}"
    return f"Failed to set layer opacity: {output}"


# ── Sprite info ─────────────────────────────────────────────────────────────


@mcp.tool()
async def get_sprite_info(filename: str) -> str:
    """Return sprite info as structured text (dimensions, frames, layers with visibility/opacity).

    Args:
        filename: Path to the Aseprite file
    """
    err = check_file(filename)
    if err:
        return err

    script = """
local spr = app.activeSprite
if not spr then return "No active sprite" end

local lines = {}
table.insert(lines, "Sprite: " .. spr.filename)
table.insert(lines, "  Dimensions: " .. spr.width .. "x" .. spr.height)
table.insert(lines, "  Frames: " .. #spr.frames)

for i, frame in ipairs(spr.frames) do
    table.insert(lines, "    Frame " .. i .. ": " .. (frame.duration * 1000) .. "ms")
end

table.insert(lines, "  Layers:")
for _, layer in ipairs(spr.layers) do
    table.insert(lines, "    " .. layer.name .. " (visible=" .. tostring(layer.visible) .. ", opacity=" .. layer.opacity .. ")")
end

if #spr.tags > 0 then
    table.insert(lines, "  Tags:")
    for _, tag in ipairs(spr.tags) do
        table.insert(lines, "    " .. tag.name .. ": frames " .. (tag.fromFrame.frameNumber) .. "-" .. (tag.toFrame.frameNumber))
    end
end

return table.concat(lines, "\\n")
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return output.strip()
    return f"Failed to get sprite info: {output}"


# ── Frame duplication ────────────────────────────────────────────────────────


@mcp.tool()
async def duplicate_frame_range(
    filename: str, start_frame: int, end_frame: int, times: int = 1
) -> str:
    """Duplicate a frame range and append copies.

    Args:
        filename: Path to the Aseprite file
        start_frame: 1-based index of the first frame to duplicate
        end_frame: 1-based index of the last frame to duplicate
        times: Number of times to duplicate the range (default: 1)
    """
    if start_frame < 1:
        return f"Error: start_frame must be >= 1, got {start_frame}"
    if end_frame < start_frame:
        return f"Error: end_frame ({end_frame}) must be >= start_frame ({start_frame})"
    if times < 1:
        return f"Error: times must be >= 1, got {times}"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {start_frame} > #spr.frames or {end_frame} > #spr.frames then
    return "Frame range exceeds total frames (" .. #spr.frames .. ")"
end

app.transaction(function()
    for t = 1, {times} do
        for i = {start_frame}, {end_frame} do
            spr:newEmptyFrame()
            local srcFrame = spr.frames[i]
            local dstFrame = spr.frames[#spr.frames]
            for _, layer in ipairs(spr.layers) do
                local srcCel = layer:cel(srcFrame)
                if srcCel then
                    local newImg = Image(srcCel.image)
                    spr:newCel(layer, dstFrame, newImg, srcCel.position)
                end
            end
        end
    end
end)

spr:saveAs("{esc}")
return "Duplicated frames {start_frame}-{end_frame} x{times}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Duplicated frames {start_frame}-{end_frame} x{times} in {filename}"
    return f"Failed to duplicate frame range: {output}"


# ── Cel position tools ──────────────────────────────────────────────────────


@mcp.tool()
async def set_cel_position(
    filename: str,
    layer_name: str,
    frame_index: int,
    x: int,
    y: int,
    create_if_missing: bool = False,
    source_frame_index: int | None = None,
) -> str:
    """Set a cel's position in a specific layer and frame.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the target layer
        frame_index: 1-based frame index
        x: New X position for the cel
        y: New Y position for the cel
        create_if_missing: If True, create a cel if none exists at the layer/frame
        source_frame_index: When creating, copy cel from this frame index (default: frame_index)
    """
    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)
    create_flag = _lua_bool(create_if_missing)
    source_frame = source_frame_index if source_frame_index is not None else frame_index

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {frame_index} > #spr.frames then
    return "Frame index {frame_index} exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

local frame = spr.frames[{frame_index}]
local cel = target:cel(frame)

if not cel and {create_flag} then
    local srcFrame = spr.frames[{source_frame}]
    local srcCel = target:cel(srcFrame)
    if srcCel then
        local newImg = Image(srcCel.image)
        cel = spr:newCel(target, frame, newImg, Point({x}, {y}))
    else
        local img = Image(spr.width, spr.height, spr.colorMode)
        cel = spr:newCel(target, frame, img, Point({x}, {y}))
    end
else
    if not cel then
        return "No cel on layer '" .. "{esc_layer}" .. "' at frame {frame_index}"
    end
    cel.position = Point({x}, {y})
end

spr:saveAs("{esc}")
return "Set cel position on layer '" .. target.name .. "' at frame {frame_index} to ({x}, {y})"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set cel position on layer '{layer_name}' at frame {frame_index} to ({x}, {y}) in {filename}"
    return f"Failed to set cel position: {output}"


@mcp.tool()
async def tween_cel_positions(
    filename: str,
    layer_name: str,
    start_frame: int,
    end_frame: int,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    create_missing_cels: bool = False,
    source_frame_index: int | None = None,
) -> str:
    """Tween cel positions linearly across a frame range.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the target layer
        start_frame: 1-based index of the first frame in the range
        end_frame: 1-based index of the last frame in the range
        start_x: X position at the start frame
        start_y: Y position at the start frame
        end_x: X position at the end frame
        end_y: Y position at the end frame
        create_missing_cels: If True, create cels where none exist
        source_frame_index: Source frame for copying cel content when creating (default: start_frame)
    """
    if start_frame < 1 or end_frame < 1:
        return "Error: frame indices must be >= 1"
    if end_frame <= start_frame:
        return f"Error: end_frame ({end_frame}) must be > start_frame ({start_frame})"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)
    create_flag = _lua_bool(create_missing_cels)
    source_frame = source_frame_index if source_frame_index is not None else start_frame

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {start_frame} > #spr.frames or {end_frame} > #spr.frames then
    return "Frame range exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

local totalSteps = {end_frame} - {start_frame}
local srcFrame = spr.frames[{source_frame}]

app.transaction(function()
    for i = {start_frame}, {end_frame} do
        local t = (i - {start_frame}) / totalSteps
        local newX = math.floor({start_x} + ({end_x} - {start_x}) * t + 0.5)
        local newY = math.floor({start_y} + ({end_y} - {start_y}) * t + 0.5)

        local frame = spr.frames[i]
        local cel = target:cel(frame)

        if cel then
            cel.position = Point(newX, newY)
        elseif {create_flag} then
            local srcCel = target:cel(srcFrame)
            if srcCel then
                local newImg = Image(srcCel.image)
                spr:newCel(target, frame, newImg, Point(newX, newY))
            else
                local img = Image(spr.width, spr.height, spr.colorMode)
                spr:newCel(target, frame, img, Point(newX, newY))
            end
        end
    end
end)

spr:saveAs("{esc}")
return "Tweened cel positions on layer '{esc_layer}' from frame {start_frame}-{end_frame}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Tweened cel positions on layer '{layer_name}' from frame {start_frame}-{end_frame} in {filename}"
    return f"Failed to tween cel positions: {output}"


@mcp.tool()
async def offset_cel_positions(
    filename: str,
    layer_name: str,
    start_frame: int,
    end_frame: int,
    dx: int,
    dy: int,
) -> str:
    """Offset cel positions by a delta across a frame range.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the target layer
        start_frame: 1-based index of the first frame in the range
        end_frame: 1-based index of the last frame in the range
        dx: Horizontal offset in pixels (can be negative)
        dy: Vertical offset in pixels (can be negative)
    """
    if start_frame < 1 or end_frame < 1:
        return "Error: frame indices must be >= 1"
    if start_frame > end_frame:
        return f"Error: start_frame ({start_frame}) must be <= end_frame ({end_frame})"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {start_frame} > #spr.frames or {end_frame} > #spr.frames then
    return "Frame range exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

app.transaction(function()
    for i = {start_frame}, {end_frame} do
        local frame = spr.frames[i]
        local cel = target:cel(frame)
        if cel then
            cel.position = Point(cel.position.x + {dx}, cel.position.y + {dy})
        end
    end
end)

spr:saveAs("{esc}")
return "Offset cel positions on layer '{esc_layer}' frames {start_frame}-{end_frame} by ({dx}, {dy})"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Offset cel positions on layer '{layer_name}' frames {start_frame}-{end_frame} by ({dx}, {dy}) in {filename}"
    return f"Failed to offset cel positions: {output}"


# ── Cel creation / deletion ──────────────────────────────────────────────────


@mcp.tool()
async def create_cel(
    filename: str, layer_name: str, frame_index: int, x: int = 0, y: int = 0
) -> str:
    """Create an empty cel on a layer/frame.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the target layer
        frame_index: 1-based frame index
        x: X position for the cel (default: 0)
        y: Y position for the cel (default: 0)
    """
    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {frame_index} > #spr.frames then
    return "Frame index {frame_index} exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

local frame = spr.frames[{frame_index}]
local existingCel = target:cel(frame)
if existingCel then
    return "Cel already exists on layer '" .. target.name .. "' at frame {frame_index}"
end

app.transaction(function()
    local img = Image(spr.width, spr.height, spr.colorMode)
    spr:newCel(target, frame, img, Point({x}, {y}))
end)

spr:saveAs("{esc}")
return "Created cel on layer '" .. target.name .. "' at frame {frame_index}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Created cel on layer '{layer_name}' at frame {frame_index} at ({x}, {y}) in {filename}"
    return f"Failed to create cel: {output}"


@mcp.tool()
async def clear_cel(filename: str, layer_name: str, frame_index: int) -> str:
    """Delete a cel on a layer/frame.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the target layer
        frame_index: 1-based frame index
    """
    if frame_index < 1:
        return f"Error: frame_index must be >= 1, got {frame_index}"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {frame_index} > #spr.frames then
    return "Frame index {frame_index} exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

local frame = spr.frames[{frame_index}]
local cel = target:cel(frame)
if not cel then
    return "No cel on layer '" .. target.name .. "' at frame {frame_index}"
end

app.transaction(function()
    spr:deleteCel(cel)
end)

spr:saveAs("{esc}")
return "Deleted cel on layer '" .. target.name .. "' at frame {frame_index}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Cleared cel on layer '{layer_name}' at frame {frame_index} in {filename}"
    return f"Failed to clear cel: {output}"


# ── Cel & frame copy ────────────────────────────────────────────────────────


@mcp.tool()
async def copy_cel(
    filename: str,
    layer_name: str,
    source_frame: int,
    target_frame: int,
    replace: bool = True,
) -> str:
    """Copy a cel from one frame to another on the same layer.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the target layer
        source_frame: 1-based index of the source frame
        target_frame: 1-based index of the target frame
        replace: If True, replace existing cel at target (default: True)
    """
    if source_frame < 1 or target_frame < 1:
        return "Error: frame indices must be >= 1"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)
    replace_flag = _lua_bool(replace)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {source_frame} > #spr.frames or {target_frame} > #spr.frames then
    return "Frame index exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

local srcCel = target:cel(spr.frames[{source_frame}])
if not srcCel then
    return "No cel on layer '" .. target.name .. "' at frame {source_frame}"
end

local dstFrame = spr.frames[{target_frame}]
local dstCel = target:cel(dstFrame)

if dstCel and not {replace_flag} then
    return "Cel already exists at target frame and replace=false"
end

app.transaction(function()
    local newImg = Image(srcCel.image)
    if dstCel then
        spr:deleteCel(dstCel)
    end
    spr:newCel(target, dstFrame, newImg, srcCel.position)
end)

spr:saveAs("{esc}")
return "Copied cel on layer '" .. target.name .. "' from frame {source_frame} to {target_frame}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Copied cel on layer '{layer_name}' from frame {source_frame} to {target_frame} in {filename}"
    return f"Failed to copy cel: {output}"


@mcp.tool()
async def copy_frame(
    filename: str,
    source_frame: int,
    target_frame: int | None = None,
    overwrite: bool = True,
) -> str:
    """Copy all cels from a source frame to a target frame (or append).

    Args:
        filename: Path to the Aseprite file
        source_frame: 1-based index of the source frame
        target_frame: 1-based index of the target frame. If None, appends new frame
        overwrite: If True, overwrite cels at target (default: True)
    """
    if source_frame < 1:
        return f"Error: source_frame must be >= 1, got {source_frame}"
    if target_frame is not None and target_frame < 1:
        return f"Error: target_frame must be >= 1, got {target_frame}"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    overwrite_flag = _lua_bool(overwrite)

    if target_frame is None:
        # Append a new frame at the end
        script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {source_frame} > #spr.frames then
    return "Source frame {source_frame} exceeds total frames (" .. #spr.frames .. ")"
end

local srcFrame = spr.frames[{source_frame}]

app.transaction(function()
    local newFrame = spr:newEmptyFrame()
    for _, layer in ipairs(spr.layers) do
        local srcCel = layer:cel(srcFrame)
        if srcCel then
            local newImg = Image(srcCel.image)
            spr:newCel(layer, newFrame, newImg, srcCel.position)
        end
    end
end)

spr:saveAs("{esc}")
return "Appended copy of frame {source_frame}"
"""
    else:
        script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {source_frame} > #spr.frames or {target_frame} > #spr.frames then
    return "Frame index exceeds total frames (" .. #spr.frames .. ")"
end

local srcFrame = spr.frames[{source_frame}]
local dstFrame = spr.frames[{target_frame}]

app.transaction(function()
    for _, layer in ipairs(spr.layers) do
        local srcCel = layer:cel(srcFrame)
        if srcCel then
            local dstCel = layer:cel(dstFrame)
            if dstCel and not {overwrite_flag} then
                -- skip, don't overwrite
            else
                if dstCel then
                    spr:deleteCel(dstCel)
                end
                local newImg = Image(srcCel.image)
                spr:newCel(layer, dstFrame, newImg, srcCel.position)
            end
        end
    end
end)

spr:saveAs("{esc}")
return "Copied frame {source_frame} to {target_frame}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        if target_frame is None:
            return f"Appended copy of frame {source_frame} in {filename}"
        return f"Copied frame {source_frame} to {target_frame} in {filename}"
    return f"Failed to copy frame: {output}"


@mcp.tool()
async def propagate_frame_to_range(
    filename: str,
    source_frame: int,
    start_frame: int,
    end_frame: int,
    overwrite: bool = True,
) -> str:
    """Copy all layers from a source frame to a range of frames.

    Args:
        filename: Path to the Aseprite file
        source_frame: 1-based index of the source frame
        start_frame: 1-based index of the first target frame in the range
        end_frame: 1-based index of the last target frame in the range
        overwrite: If True, overwrite existing cels at target frames (default: True)
    """
    if source_frame < 1 or start_frame < 1 or end_frame < 1:
        return "Error: frame indices must be >= 1"
    if start_frame > end_frame:
        return f"Error: start_frame ({start_frame}) must be <= end_frame ({end_frame})"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    overwrite_flag = _lua_bool(overwrite)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {source_frame} > #spr.frames or {start_frame} > #spr.frames or {end_frame} > #spr.frames then
    return "Frame index exceeds total frames (" .. #spr.frames .. ")"
end

local srcFrame = spr.frames[{source_frame}]

app.transaction(function()
    for i = {start_frame}, {end_frame} do
        if i ~= {source_frame} then
            local dstFrame = spr.frames[i]
            for _, layer in ipairs(spr.layers) do
                local srcCel = layer:cel(srcFrame)
                if srcCel then
                    local dstCel = layer:cel(dstFrame)
                    if dstCel and not {overwrite_flag} then
                        -- skip
                    else
                        if dstCel then
                            spr:deleteCel(dstCel)
                        end
                        local newImg = Image(srcCel.image)
                        spr:newCel(layer, dstFrame, newImg, srcCel.position)
                    end
                end
            end
        end
    end
end)

spr:saveAs("{esc}")
return "Propagated frame {source_frame} to frames {start_frame}-{end_frame}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Propagated frame {source_frame} to frames {start_frame}-{end_frame} in {filename}"
    return f"Failed to propagate frame: {output}"


# ── Tag tools ────────────────────────────────────────────────────────────────


@mcp.tool()
async def set_tag(
    filename: str,
    name: str,
    from_frame: int,
    to_frame: int,
    direction: str = "forward",
) -> str:
    """Create or update an animation tag.

    Args:
        filename: Path to the Aseprite file
        name: Tag name
        from_frame: 1-based index of the first frame in the tag
        to_frame: 1-based index of the last frame in the tag
        direction: Animation direction - "forward", "reverse", or "pingpong" (default: "forward")
    """
    valid_directions = {"forward", "reverse", "pingpong"}
    if direction not in valid_directions:
        return f"Error: direction must be one of {valid_directions}, got '{direction}'"
    if from_frame < 1 or to_frame < 1:
        return "Error: frame indices must be >= 1"
    if from_frame > to_frame:
        return f"Error: from_frame ({from_frame}) must be <= to_frame ({to_frame})"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_name = _lua_escape(name)

    # Map direction string to Lua enum value
    dir_map = {
        "forward": "AniDir.FORWARD",
        "reverse": "AniDir.REVERSE",
        "pingpong": "AniDir.PINGPONG",
    }
    dir_lua = dir_map[direction]

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {from_frame} > #spr.frames or {to_frame} > #spr.frames then
    return "Frame range exceeds total frames (" .. #spr.frames .. ")"
end

app.transaction(function()
    local existingTag = nil
    for _, tag in ipairs(spr.tags) do
        if tag.name == "{esc_name}" then
            existingTag = tag
            break
        end
    end

    if existingTag then
        existingTag.fromFrame = spr.frames[{from_frame}]
        existingTag.toFrame = spr.frames[{to_frame}]
        existingTag.aniDir = {dir_lua}
    else
        local newTag = spr:newTag(spr.frames[{from_frame}], spr.frames[{to_frame}])
        newTag.name = "{esc_name}"
        newTag.aniDir = {dir_lua}
    end
end)

spr:saveAs("{esc}")
return "Set tag '{esc_name}' frames {from_frame}-{to_frame} direction {direction}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set tag '{name}' frames {from_frame}-{to_frame} direction {direction} in {filename}"
    return f"Failed to set tag: {output}"


# ── Eased tweening ───────────────────────────────────────────────────────────


@mcp.tool()
async def tween_cel_positions_eased(
    filename: str,
    layer_name: str,
    start_frame: int,
    end_frame: int,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    easing: str = "smoothstep",
    create_missing_cels: bool = False,
    source_frame_index: int | None = None,
) -> str:
    """Tween cel positions with easing across a frame range.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the target layer
        start_frame: 1-based index of the first frame in the range
        end_frame: 1-based index of the last frame in the range
        start_x: X position at the start frame
        start_y: Y position at the start frame
        end_x: X position at the end frame
        end_y: Y position at the end frame
        easing: Easing function - "linear", "ease_in", "ease_out", "ease_in_out", or "smoothstep" (default: "smoothstep")
        create_missing_cels: If True, create cels where none exist
        source_frame_index: Source frame for copying cel content when creating (default: start_frame)
    """
    valid_easings = {"linear", "ease_in", "ease_out", "ease_in_out", "smoothstep"}
    if easing not in valid_easings:
        return f"Error: easing must be one of {valid_easings}, got '{easing}'"
    if start_frame < 1 or end_frame < 1:
        return "Error: frame indices must be >= 1"
    if end_frame <= start_frame:
        return f"Error: end_frame ({end_frame}) must be > start_frame ({start_frame})"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)
    create_flag = _lua_bool(create_missing_cels)
    source_frame = source_frame_index if source_frame_index is not None else start_frame

    # Build the easing function Lua code
    easing_lua = {
        "linear": "local function ease(t) return t end",
        "ease_in": "local function ease(t) return t * t * t end",
        "ease_out": "local function ease(t) return 1 - (1 - t) ^ 3 end",
        "ease_in_out": "local function ease(t) if t < 0.5 then return 4 * t * t * t else return 1 - ((-2 * t + 2) ^ 3) / 2 end end",
        "smoothstep": "local function ease(t) return t * t * (3 - 2 * t) end",
    }[easing]

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {start_frame} > #spr.frames or {end_frame} > #spr.frames then
    return "Frame range exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

{easing_lua}

local totalSteps = {end_frame} - {start_frame}
local srcFrame = spr.frames[{source_frame}]

app.transaction(function()
    for i = {start_frame}, {end_frame} do
        local t = (i - {start_frame}) / totalSteps
        local et = ease(t)
        local newX = math.floor({start_x} + ({end_x} - {start_x}) * et + 0.5)
        local newY = math.floor({start_y} + ({end_y} - {start_y}) * et + 0.5)

        local frame = spr.frames[i]
        local cel = target:cel(frame)

        if cel then
            cel.position = Point(newX, newY)
        elseif {create_flag} then
            local srcCel = target:cel(srcFrame)
            if srcCel then
                local newImg = Image(srcCel.image)
                spr:newCel(target, frame, newImg, Point(newX, newY))
            else
                local img = Image(spr.width, spr.height, spr.colorMode)
                spr:newCel(target, frame, img, Point(newX, newY))
            end
        end
    end
end)

spr:saveAs("{esc}")
return "Tweened cel positions with '{easing}' easing on layer '{esc_layer}'"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Tweened cel positions with '{easing}' easing on layer '{layer_name}' frames {start_frame}-{end_frame} in {filename}"
    return f"Failed to tween cel positions: {output}"


@mcp.tool()
async def oscillate_cel_positions(
    filename: str,
    layer_name: str,
    start_frame: int,
    end_frame: int,
    amplitude_x: int = 0,
    amplitude_y: int = 0,
    cycles: float = 1.0,
    phase_deg: float = 0.0,
    create_missing_cels: bool = False,
    source_frame_index: int | None = None,
) -> str:
    """Oscillate cel positions using a sine wave across a frame range.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the target layer
        start_frame: 1-based index of the first frame in the range
        end_frame: 1-based index of the last frame in the range
        amplitude_x: X amplitude of oscillation in pixels (default: 0)
        amplitude_y: Y amplitude of oscillation in pixels (default: 0)
        cycles: Number of complete sine wave cycles (default: 1.0)
        phase_deg: Phase offset in degrees (default: 0.0)
        create_missing_cels: If True, create cels where none exist
        source_frame_index: Source frame for copying cel content when creating (default: start_frame)
    """
    if start_frame < 1 or end_frame < 1:
        return "Error: frame indices must be >= 1"
    if end_frame <= start_frame:
        return f"Error: end_frame ({end_frame}) must be > start_frame ({start_frame})"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)
    create_flag = _lua_bool(create_missing_cels)
    source_frame = source_frame_index if source_frame_index is not None else start_frame
    phase_rad = phase_deg * (3.14159265358979323846 / 180.0)

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {start_frame} > #spr.frames or {end_frame} > #spr.frames then
    return "Frame range exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

local totalSteps = {end_frame} - {start_frame}
local srcFrame = spr.frames[{source_frame}]
local phaseRad = {phase_rad}
local cycles = {cycles}
local ampX = {amplitude_x}
local ampY = {amplitude_y}

-- Store original positions on first pass
local origPositions = {{}}
for i = {start_frame}, {end_frame} do
    local frame = spr.frames[i]
    local cel = target:cel(frame)
    if cel then
        origPositions[i] = {{ x = cel.position.x, y = cel.position.y }}
    end
end

app.transaction(function()
    for i = {start_frame}, {end_frame} do
        local t = (i - {start_frame}) / totalSteps
        local angle = 2 * math.pi * cycles * t + phaseRad
        local offsetX = math.floor(ampX * math.sin(angle) + 0.5)
        local offsetY = math.floor(ampY * math.sin(angle) + 0.5)

        local frame = spr.frames[i]
        local cel = target:cel(frame)

        if cel then
            local origX = origPositions[i] and origPositions[i].x or cel.position.x
            local origY = origPositions[i] and origPositions[i].y or cel.position.y
            cel.position = Point(origX + offsetX, origY + offsetY)
        elseif {create_flag} then
            local srcCel = target:cel(srcFrame)
            local baseX = 0
            local baseY = 0
            if srcCel then
                baseX = srcCel.position.x
                baseY = srcCel.position.y
                local newImg = Image(srcCel.image)
                spr:newCel(target, frame, newImg, Point(baseX + offsetX, baseY + offsetY))
            else
                local img = Image(spr.width, spr.height, spr.colorMode)
                spr:newCel(target, frame, img, Point(offsetX, offsetY))
            end
        end
    end
end)

spr:saveAs("{esc}")
return "Oscillated cel positions on layer '{esc_layer}'"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return (
            f"Oscillated cel positions on layer '{layer_name}' frames "
            f"{start_frame}-{end_frame} (amp=({amplitude_x},{amplitude_y}), "
            f"cycles={cycles}, phase={phase_deg}°) in {filename}"
        )
    return f"Failed to oscillate cel positions: {output}"


@mcp.tool()
async def tween_cel_opacity_eased(
    filename: str,
    layer_name: str,
    start_frame: int,
    end_frame: int,
    start_opacity: int,
    end_opacity: int,
    easing: str = "smoothstep",
    create_missing_cels: bool = False,
    source_frame_index: int | None = None,
) -> str:
    """Tween cel opacity with easing across a frame range.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the target layer
        start_frame: 1-based index of the first frame
        end_frame: 1-based index of the last frame
        start_opacity: Opacity at start (0-255)
        end_opacity: Opacity at end (0-255)
        easing: Easing function - "linear", "ease_in", "ease_out", "ease_in_out", or "smoothstep" (default: "smoothstep")
        create_missing_cels: If True, create cels where none exist
        source_frame_index: Source frame for copying cel content when creating (default: start_frame)
    """
    valid_easings = {"linear", "ease_in", "ease_out", "ease_in_out", "smoothstep"}
    if easing not in valid_easings:
        return f"Error: easing must be one of {valid_easings}, got '{easing}'"
    if not (0 <= start_opacity <= 255):
        return f"Error: start_opacity must be 0-255, got {start_opacity}"
    if not (0 <= end_opacity <= 255):
        return f"Error: end_opacity must be 0-255, got {end_opacity}"
    if start_frame < 1 or end_frame < 1:
        return "Error: frame indices must be >= 1"
    if end_frame <= start_frame:
        return f"Error: end_frame ({end_frame}) must be > start_frame ({start_frame})"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    esc_layer = _lua_escape(layer_name)
    create_flag = _lua_bool(create_missing_cels)
    source_frame = source_frame_index if source_frame_index is not None else start_frame

    easing_lua = {
        "linear": "local function ease(t) return t end",
        "ease_in": "local function ease(t) return t * t * t end",
        "ease_out": "local function ease(t) return 1 - (1 - t) ^ 3 end",
        "ease_in_out": "local function ease(t) if t < 0.5 then return 4 * t * t * t else return 1 - ((-2 * t + 2) ^ 3) / 2 end end",
        "smoothstep": "local function ease(t) return t * t * (3 - 2 * t) end",
    }[easing]

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {start_frame} > #spr.frames or {end_frame} > #spr.frames then
    return "Frame range exceeds total frames (" .. #spr.frames .. ")"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{esc_layer}" then
        target = layer
        break
    end
end

if not target then
    return "Layer '" .. "{esc_layer}" .. "' not found"
end

{easing_lua}

local totalSteps = {end_frame} - {start_frame}
local srcFrame = spr.frames[{source_frame}]

app.transaction(function()
    for i = {start_frame}, {end_frame} do
        local t = (i - {start_frame}) / totalSteps
        local et = ease(t)
        local opacity = math.floor({start_opacity} + ({end_opacity} - {start_opacity}) * et + 0.5)
        if opacity < 0 then opacity = 0 end
        if opacity > 255 then opacity = 255 end

        local frame = spr.frames[i]
        local cel = target:cel(frame)

        if cel then
            cel.opacity = opacity
        elseif {create_flag} then
            local srcCel = target:cel(srcFrame)
            if srcCel then
                local newImg = Image(srcCel.image)
                local newCel = spr:newCel(target, frame, newImg, srcCel.position)
                newCel.opacity = opacity
            else
                local img = Image(spr.width, spr.height, spr.colorMode)
                local newCel = spr:newCel(target, frame, img, Point(0, 0))
                newCel.opacity = opacity
            end
        end
    end
end)

spr:saveAs("{esc}")
return "Tweened cel opacity with '{easing}' easing on layer '{esc_layer}'"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return (
            f"Tweened cel opacity with '{easing}' easing on layer '{layer_name}' "
            f"frames {start_frame}-{end_frame} ({start_opacity}->{end_opacity}) in {filename}"
        )
    return f"Failed to tween cel opacity: {output}"


# ── Cel propagation ─────────────────────────────────────────────────────────


@mcp.tool()
async def propagate_cels(
    filename: str,
    layer_names: list[str],
    source_frame: int,
    start_frame: int,
    end_frame: int,
    replace: bool = True,
) -> str:
    """Copy cels from a source frame to a range of frames for specific layers.

    Args:
        filename: Path to the Aseprite file
        layer_names: List of layer names to propagate
        source_frame: 1-based index of the source frame
        start_frame: 1-based index of the first target frame
        end_frame: 1-based index of the last target frame
        replace: If True, overwrite existing cels (default: True)
    """
    if source_frame < 1 or start_frame < 1 or end_frame < 1:
        return "Error: frame indices must be >= 1"
    if start_frame > end_frame:
        return f"Error: start_frame ({start_frame}) must be <= end_frame ({end_frame})"
    err = check_file(filename)
    if err:
        return err

    esc = _esc_path(filename)
    replace_flag = _lua_bool(replace)

    # Build Lua table of layer names
    layer_table_items = ", ".join(f'"{_lua_escape(n)}"' for n in layer_names)
    layer_table = f"{{{layer_table_items}}}"

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

if {source_frame} > #spr.frames or {start_frame} > #spr.frames or {end_frame} > #spr.frames then
    return "Frame index exceeds total frames (" .. #spr.frames .. ")"
end

local layerNames = {layer_table}

-- Build set of target layer names
local targetNames = {{}}
for _, name in ipairs(layerNames) do
    targetNames[name] = true
end

-- Find matching layers
local layers = {{}}
for _, layer in ipairs(spr.layers) do
    if targetNames[layer.name] then
        table.insert(layers, layer)
    end
end

if #layers == 0 then
    return "No matching layers found"
end

local srcFrame = spr.frames[{source_frame}]

app.transaction(function()
    for i = {start_frame}, {end_frame} do
        if i ~= {source_frame} then
            local dstFrame = spr.frames[i]
            for _, layer in ipairs(layers) do
                local srcCel = layer:cel(srcFrame)
                if srcCel then
                    local dstCel = layer:cel(dstFrame)
                    if dstCel and not {replace_flag} then
                        -- skip
                    else
                        if dstCel then
                            spr:deleteCel(dstCel)
                        end
                        local newImg = Image(srcCel.image)
                        spr:newCel(layer, dstFrame, newImg, srcCel.position)
                    end
                end
            end
        end
    end
end)

spr:saveAs("{esc}")
return "Propagated cels from frame {source_frame} to frames {start_frame}-{end_frame}"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        layers_str = ", ".join(f"'{n}'" for n in layer_names)
        return (
            f"Propagated cels on layers [{layers_str}] from frame {source_frame} "
            f"to frames {start_frame}-{end_frame} in {filename}"
        )
    return f"Failed to propagate cels: {output}"