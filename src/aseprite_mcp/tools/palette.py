"""Palette tools for Aseprite MCP — color palette management."""

from __future__ import annotations

import json

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import (
    _lua_escape,
    check_file,
    get_cli,
    validate_hex_color,
)


@mcp.tool()
async def get_palette(filename: str) -> str:
    """Get the color palette from a sprite file.

    Args:
        filename: Path to the Aseprite file
    """
    err = check_file(filename)
    if err:
        return err

    script = """
local spr = app.activeSprite
if not spr then print("ERROR:No active sprite") return end

local ok, pal = pcall(function() return spr.palettes[1] end)
if not ok or not pal then print("ERROR:No palette found") return end

local size = #pal
local parts = {}
table.insert(parts, "[")
for i = 0, size - 1 do
    local c = pal:getColor(i)
    local hex = string.format("#%02X%02X%02X", c.red, c.green, c.blue)
    table.insert(parts, '"' .. hex .. '"')
    if i < size - 1 then
        table.insert(parts, ",")
    end
end
table.insert(parts, "]")
print(table.concat(parts))
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if not success:
        return f"Failed to get palette: {output}"

    # Parse the palette output
    for line in output.strip().splitlines():
        line = line.strip()
        if line.startswith("ERROR:"):
            return f"Error: {line[6:]}"
        if line.startswith("["):
            try:
                colors = json.loads(line)
                return json.dumps({"palette": colors, "count": len(colors)})
            except json.JSONDecodeError:
                pass

    return f"Failed to parse palette data from output: {output}"


@mcp.tool()
async def set_palette(filename: str, colors: list[str]) -> str:
    """Set the color palette of a sprite.

    Args:
        filename: Path to the Aseprite file
        colors: List of hex color strings (e.g. ["#ff0000", "#00ff00", "#0000ff"])
    """
    err = check_file(filename)
    if err:
        return err

    if not colors:
        return "Error: colors list must not be empty"

    # Validate and parse all colors
    parsed = []
    for i, color in enumerate(colors):
        result = validate_hex_color(color)
        if result is None:
            return (
                f"Error: invalid hex color at index {i}: "
                f"'{color}' (expected format #RRGGBB)"
            )
        parsed.append(result)

    # Build Lua palette color entries
    color_lines = []
    for i, (r, g, b) in enumerate(parsed):
        color_lines.append(
            f"    pal:setColor({i}, Color({r}, {g}, {b}, 255))"
        )
    color_code = "\n".join(color_lines)

    safe_filename = _lua_escape(filename.replace("\\", "/"))

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

local pal = Palette({len(parsed)})
{color_code}

app.transaction(function()
    spr:setPalette(pal)
end)

spr:saveAs("{safe_filename}")
return "Palette set"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Set palette with {len(parsed)} colors in '{filename}'"
    return f"Failed to set palette: {output}"


@mcp.tool()
async def remap_colors_in_cel_range(
    filename: str,
    layer_name: str,
    start_frame: int,
    end_frame: int,
    mappings: list[dict[str, str]],
    create_missing_cels: bool = False,
    source_frame_index: int | None = None,
) -> str:
    """Remap colors in a range of cels by replacing source colors with target colors.

    Args:
        filename: Path to the Aseprite file
        layer_name: Name of the layer to remap colors in
        start_frame: Starting frame index (1-based)
        end_frame: Ending frame index (1-based, inclusive)
        mappings: List of color mappings, each with "from" and "to" hex color strings
        create_missing_cels: If True, create cels that don't exist. Default: False
        source_frame_index: If set, use this frame as source for
            new cel images. Default: None
    """
    err = check_file(filename)
    if err:
        return err

    if start_frame < 1:
        return f"Error: start_frame must be >= 1, got {start_frame}"
    if end_frame < start_frame:
        return (
            f"Error: end_frame must be >= start_frame, "
            f"got end_frame={end_frame}, start_frame={start_frame}"
        )

    # Parse all color mappings
    parsed_mappings = []
    for i, m in enumerate(mappings):
        src = validate_hex_color(m.get("from", ""))
        dst = validate_hex_color(m.get("to", ""))
        if src is None:
            return (
                f"Error: invalid 'from' hex color at mapping {i}: "
                f"'{m.get('from', '')}'"
            )
        if dst is None:
            return (
                f"Error: invalid 'to' hex color at mapping {i}: "
                f"'{m.get('to', '')}'"
            )
        parsed_mappings.append((src, dst))

    safe_layer_name = _lua_escape(layer_name)
    safe_filename = _lua_escape(filename.replace("\\", "/"))

    # Build Lua table of color mappings [src_r, src_g, src_b, dst_r, dst_g, dst_b]
    mapping_entries = []
    for (sr, sg, sb), (dr, dg, db) in parsed_mappings:
        mapping_entries.append(f"  {{{sr}, {sg}, {sb}, {dr}, {dg}, {db}}}")
    mapping_table = ",\n".join(mapping_entries)

    create_flag = "true" if create_missing_cels else "false"
    source_frame_lua = (
        str(source_frame_index) if source_frame_index is not None else "nil"
    )

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

local start_idx = {start_frame}
local end_idx = {end_frame}
if start_idx < 1 or end_idx > #spr.frames or start_idx > end_idx then
    return "Frame range out of bounds"
end

local target = nil
for _, layer in ipairs(spr.layers) do
    if layer.name == "{safe_layer_name}" then
        target = layer
        break
    end
end
if not target then return "Layer not found" end

local source_frame = {source_frame_lua}
if source_frame == nil then
    source_frame = start_idx
end
if source_frame < 1 or source_frame > #spr.frames then
    return "Source frame out of range"
end

local colorMap = {{
{mapping_table}
}}

local pixelMatchCount = 0

app.transaction(function()
    for fi = start_idx, end_idx do
        local frame = spr.frames[fi]
        local cel = target:cel(frame)

        if not cel and {create_flag} then
            local source_cel = target:cel(spr.frames[source_frame])
            if source_cel then
                local img = source_cel.image:clone()
                cel = spr:newCel(target, frame, img, source_cel.position)
            else
                local img = Image(spr.width, spr.height, spr.colorMode)
                cel = spr:newCel(target, frame, img, Point(0, 0))
            end
        end

        if cel and cel.image then
            local img = cel.image
            for y = 0, img.height - 1 do
                for x = 0, img.width - 1 do
                    local c = img:getPixel(x, y)
                    local r = app.pixelColor.rgbaR(c)
                    local g = app.pixelColor.rgbaG(c)
                    local b = app.pixelColor.rgbaB(c)
                    local a = app.pixelColor.rgbaA(c)
                    if a > 0 then
                        for _, m in ipairs(colorMap) do
                            if r == m[1] and g == m[2] and b == m[3] then
                                local nc = app.pixelColor.rgba(m[4], m[5], m[6], a)
                                img:putPixel(x, y, nc)
                                pixelMatchCount = pixelMatchCount + 1
                                break
                            end
                        end
                    end
                end
            end
        end
    end
end)

spr:saveAs("{safe_filename}")
return "Colors remapped in " .. pixelMatchCount .. " pixels"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Remapped colors in '{filename}' layer '{layer_name}'"
    return f"Failed to remap colors: {output}"
