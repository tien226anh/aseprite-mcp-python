"""Scene tools for Aseprite MCP — layer and cel management across sprites."""

from __future__ import annotations

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import get_cli, check_file, _lua_escape


@mcp.tool()
async def copy_layers_between_sprites(
    source_filename: str,
    target_filename: str,
    layer_names: list[str],
    replace: bool = True,
    create_missing_frames: bool = True,
) -> str:
    """Copy one or more layers (with their cels) from a source sprite to a target sprite.

    Args:
        source_filename: Path to the source Aseprite file.
        target_filename: Path to the target Aseprite file.
        layer_names: List of layer names to copy from source to target.
        replace: If True, overwrite existing layers in target that share the same name.
        create_missing_frames: If True, add frames to target if it has fewer frames than source.
    """
    # Path traversal check
    for fn in (source_filename, target_filename):
        if ".." in fn:
            return f"Error: filename must not contain '..' (path traversal): {fn}"

    err = check_file(source_filename)
    if err:
        return err
    err = check_file(target_filename)
    if err:
        return err

    if not layer_names:
        return "Error: layer_names must not be empty"

    escaped_src = _lua_escape(source_filename.replace("\\", "/"))
    escaped_dst = _lua_escape(target_filename.replace("\\", "/"))

    # Build Lua table from layer_names list
    layer_table_entries = ", ".join(
        f'"{_lua_escape(name)}"' for name in layer_names
    )
    layer_table = "{" + layer_table_entries + "}"

    replace_flag = "true" if replace else "false"
    create_frames_flag = "true" if create_missing_frames else "false"

    script = f"""
local src = app.open("{escaped_src}")
if not src then
    return "Error: could not open source sprite"
end

local dst = app.open("{escaped_dst}")
if not dst then
    src:close()
    return "Error: could not open target sprite"
end

local layer_names = {layer_table}
local replace = {replace_flag}
local create_missing_frames = {create_frames_flag}

local copied = 0
local skipped = 0

for _, lname in ipairs(layer_names) do
    -- Find source layer
    local src_layer = nil
    for _, lyr in ipairs(src.layers) do
        if lyr.name == lname then
            src_layer = lyr
            break
        end
    end
    if not src_layer then
        skipped = skipped + 1
        goto continue_layer
    end

    -- Find or create target layer
    local dst_layer = nil
    for _, lyr in ipairs(dst.layers) do
        if lyr.name == lname then
            dst_layer = lyr
            break
        end
    end

    if dst_layer then
        if not replace then
            skipped = skipped + 1
            goto continue_layer
        end
    else
        dst_layer = dst:newLayer()
        dst_layer.name = lname
    end

    -- Create missing frames in target if needed
    if create_missing_frames then
        local src_frames = #src.frames
        local dst_frames = #dst.frames
        while #dst.frames < src_frames do
            dst:newEmptyFrame()
        end
    end

    -- Copy cels from source layer to target layer for each frame
    for fi = 1, #src.frames do
        if fi > #dst.frames then
            break
        end

        local src_cel = src_layer:cel(fi)
        if src_cel then
            local dst_cel = dst_layer:cel(fi)
            if not dst_cel then
                dst_cel = dst:newCel(dst_layer, dst.frames[fi])
            end

            -- Copy image pixels
            local src_img = src_cel.image
            local new_img = Image(src_img.width, src_img.height, src_img.colorMode)
            for y = 0, src_img.height - 1 do
                for x = 0, src_img.width - 1 do
                    new_img:drawPixel(x, y, src_img:getPixel(x, y))
                end
            end

            app.transaction(function()
                dst_cel.image = new_img
                dst_cel.position = src_cel.position
                dst_cel.opacity = src_cel.opacity
            end)
        end
    end

    copied = copied + 1

    ::continue_layer::
end

dst:saveAs(dst.filename)
src:close()
dst:close()

return "Copied " .. copied .. " layer(s), skipped " .. skipped
"""

    success, output = get_cli().execute_lua_script(script)
    if success:
        return f"Copied layers from {source_filename} to {target_filename}: {output.strip()}"
    return f"Failed to copy layers: {output}"