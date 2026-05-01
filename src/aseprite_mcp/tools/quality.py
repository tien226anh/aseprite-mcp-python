"""Quality tools for Aseprite MCP — validation, audit, and sanitization."""

from __future__ import annotations

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import _lua_escape, check_file, get_cli

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_layer_frame_ranges(layer_frame_ranges: list[str] | None) -> str:
    """Parse ["layer:1-8,17-24", "clouds:1-12"] into a Lua table string.

    Returns something like: {["layer"]={{1,8},{17,24}},["clouds"]={{1,12}},}
    """
    if not layer_frame_ranges:
        return "{}"

    entries: list[str] = []
    for entry in layer_frame_ranges:
        parts = entry.split(":", 1)
        if len(parts) != 2:
            continue
        layer_name = _lua_escape(parts[0].strip())
        ranges_str = parts[1].strip()

        range_pairs: list[str] = []
        for rng in ranges_str.split(","):
            rng = rng.strip()
            if "-" in rng:
                bounds = rng.split("-", 1)
                start = int(bounds[0].strip())
                end = int(bounds[1].strip())
                range_pairs.append("{" + str(start) + "," + str(end) + "}")
            else:
                val = int(rng)
                range_pairs.append("{" + str(val) + "," + str(val) + "}")

        entries.append('["' + layer_name + '"]={' + ",".join(range_pairs) + "}")

    return "{" + ",".join(entries) + ",}"


def _parse_overlap_pairs(overlap_pairs: list[str] | None) -> str:
    """Parse ["layerA,layerB", "layerC:layerD"] into a Lua table string.

    Returns something like: {{"layerA","layerB"},{"layerC","layerD"}}
    """
    if not overlap_pairs:
        return "{}"

    pairs: list[str] = []
    for entry in overlap_pairs:
        # Support both comma and colon as separator
        for sep in (",", ":"):
            if sep in entry:
                parts = entry.split(sep, 1)
                a = _lua_escape(parts[0].strip())
                b = _lua_escape(parts[1].strip())
                pairs.append('{"' + a + '","' + b + '"}')
                break

    return "{" + ",".join(pairs) + "}"


# ---------------------------------------------------------------------------
# Tool: ensure_layers_present
# ---------------------------------------------------------------------------


@mcp.tool()
async def ensure_layers_present(
    filename: str,
    layer_names: list[str],
    start_frame: int = 1,
    end_frame: int | None = None,
) -> str:
    """Ensure cels exist for specified layers across a frame range.

    Creates empty Image cels for any layer/frame combination where a cel is
    missing. Useful for normalising sprites before animation audit or batch
    operations.

    Args:
        filename: Path to the Aseprite file.
        layer_names: List of layer names to ensure cels for (must not be empty).
        start_frame: First frame (1-based, inclusive). Default 1.
        end_frame: Last frame (1-based, inclusive). None = last frame.
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"
    if not layer_names:
        return "Error: layer_names must not be empty"

    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    end_lua = str(end_frame) if end_frame is not None else "nil"
    layer_table_entries = ", ".join(
        '"' + _lua_escape(name) + '"' for name in layer_names
    )
    layer_table = "{" + layer_table_entries + "}"

    script = (
        'local spr = app.open("' + escaped_filename + '")\n'
        'if not spr then return "Error: could not open sprite" end\n'
        "\n"
        "local layer_names = " + layer_table + "\n"
        "local start_idx = " + str(start_frame) + "\n"
        "local end_idx = " + end_lua + "\n"
        "if end_idx == nil then end_idx = #spr.frames end\n"
        "if start_idx < 1 then start_idx = 1 end\n"
        "if end_idx > #spr.frames then end_idx = #spr.frames end\n"
        "\n"
        "local created = 0\n"
        "local skipped = 0\n"
        "\n"
        "-- Build lookup of existing layers by name\n"
        "local layer_lookup = {}\n"
        "for _, layer in ipairs(spr.layers) do\n"
        "    layer_lookup[layer.name] = layer\n"
        "end\n"
        "\n"
        "app.transaction(function()\n"
        "    for _, lname in ipairs(layer_names) do\n"
        "        local layer = layer_lookup[lname]\n"
        "        if not layer then\n"
        "            skipped = skipped + 1\n"
        "            goto continue_layer\n"
        "        end\n"
        "\n"
        "        for fi = start_idx, end_idx do\n"
        "            local frame = spr.frames[fi]\n"
        "            local cel = layer:cel(frame)\n"
        "            if not cel then\n"
        "                local img = Image(spr.width, spr.height, spr.colorMode)\n"
        "                spr:newCel(layer, frame, img, Point(0, 0))\n"
        "                created = created + 1\n"
        "            end\n"
        "        end\n"
        "\n"
        "        ::continue_layer::\n"
        "    end\n"
        "end)\n"
        "\n"
        "spr:saveAs(spr.filename)\n"
        "spr:close()\n"
        "\n"
        'return "Created " .. created .. " cel(s), '
        'skipped " .. skipped .. " layer(s)"\n'
    )

    success, output = get_cli().execute_lua_script(script)
    if success:
        return "ensure_layers_present: " + output.strip()
    return "Failed to ensure layers present: " + output


# ---------------------------------------------------------------------------
# Tool: validate_scene
# ---------------------------------------------------------------------------


@mcp.tool()
async def validate_scene(
    filename: str,
    required_layers: list[str],
    start_frame: int = 1,
    end_frame: int | None = None,
) -> str:
    """Validate presence of layers and cels across a frame range.

    Returns JSON with: frames count, range, missing_layers list, missing_cels list.

    Args:
        filename: Path to the Aseprite file.
        required_layers: List of layer names that must exist (must not be empty).
        start_frame: First frame (1-based, inclusive). Default 1.
        end_frame: Last frame (1-based, inclusive). None = last frame.
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"
    if not required_layers:
        return "Error: required_layers must not be empty"

    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    end_lua = str(end_frame) if end_frame is not None else "nil"
    layer_table_entries = ", ".join(
        '"' + _lua_escape(name) + '"' for name in required_layers
    )
    layer_table = "{" + layer_table_entries + "}"

    script = (
        'local spr = app.open("' + escaped_filename + '")\n'
        'if not spr then return "Error: could not open sprite" end\n'
        "\n"
        "local layer_names = " + layer_table + "\n"
        "local start_idx = " + str(start_frame) + "\n"
        "local end_idx = " + end_lua + "\n"
        "if end_idx == nil then end_idx = #spr.frames end\n"
        "if start_idx < 1 then start_idx = 1 end\n"
        "if end_idx > #spr.frames then end_idx = #spr.frames end\n"
        "\n"
        "local total_frames = #spr.frames\n"
        "\n"
        "-- Build layer lookup\n"
        "local layer_lookup = {}\n"
        "for _, layer in ipairs(spr.layers) do\n"
        "    layer_lookup[layer.name] = layer\n"
        "end\n"
        "\n"
        "-- Find missing layers\n"
        "local missing_layers = {}\n"
        "local found_layers = {}\n"
        "for _, lname in ipairs(layer_names) do\n"
        "    if layer_lookup[lname] then\n"
        "        table.insert(found_layers, lname)\n"
        "    else\n"
        "        table.insert(missing_layers, lname)\n"
        "    end\n"
        "end\n"
        "\n"
        "-- Find missing cels\n"
        "local missing_cels = {}\n"
        "for _, lname in ipairs(found_layers) do\n"
        "    local layer = layer_lookup[lname]\n"
        "    for fi = start_idx, end_idx do\n"
        "        local frame = spr.frames[fi]\n"
        "        local cel = layer:cel(frame)\n"
        "        if not cel then\n"
        '            table.insert(missing_cels, {layer = lname, frame = fi})\n'
        "        end\n"
        "    end\n"
        "end\n"
        "\n"
        "-- Build JSON manually using table.concat\n"
        "local parts = {}\n"
        'table.insert(parts, \'{"frames":\' .. total_frames)\n'
        'table.insert(parts, \',"range":{"start":\' '
        '.. start_idx .. \',"end":\' .. end_idx .. \'}\')\n'
        "-- missing_layers array\n"
        "local ml_parts = {}\n"
        "for i, name in ipairs(missing_layers) do\n"
        '    ml_parts[i] = \'"\' .. name .. \'"\'\n'
        "end\n"
        'table.insert(parts, \',"missing_layers":[\' '
        '.. table.concat(ml_parts, \",\") .. \']\')\n'
        "-- missing_cels array\n"
        "local mc_parts = {}\n"
        "for i, mc in ipairs(missing_cels) do\n"
        '    mc_parts[i] = \'{"layer":"\' '
        '.. mc.layer .. \'","frame":\' .. mc.frame .. \'}\'\n'
        "end\n"
        'table.insert(parts, \',"missing_cels\":[\' '
        '.. table.concat(mc_parts, \",\") .. \']\')\n'
        'table.insert(parts, \'}\')\n'
        "\n"
        "spr:close()\n"
        "\n"
        'print("JSON_START" .. table.concat(parts))\n'
    )

    success, output = get_cli().execute_lua_script(script)
    if success:
        return output.strip()
    return "Failed to validate scene: " + output


# ---------------------------------------------------------------------------
# Tool: audit_animation
# ---------------------------------------------------------------------------


@mcp.tool()
async def audit_animation(
    filename: str,
    start_frame: int = 1,
    end_frame: int | None = None,
    layer_names: list[str] | None = None,
    overlap_pairs: list[str] | None = None,
    layer_frame_ranges: list[str] | None = None,
    report_cels: bool = False,
    report_bounds: bool = False,
    max_overlaps: int = 200,
    max_out_of_range: int = 200,
) -> str:
    """Audit animation frames for overlaps and out-of-range layer activity.

    Returns JSON with: frames, summary (total_layers, layers_checked, total_cels,
    overlaps count, out_of_range count), overlaps samples, out_of_range entries.

    Args:
        filename: Path to the Aseprite file.
        start_frame: First frame (1-based, inclusive). Default 1.
        end_frame: Last frame (1-based, inclusive). None = last frame.
        layer_names: Only audit these layers. None = all layers.
        overlap_pairs: Layer pairs to check for overlapping pixels,
            e.g. ["layerA,layerB"].
        layer_frame_ranges: Expected frame ranges per layer, e.g. ["clouds:1-12"].
            Cels outside these ranges are reported as out-of-range.
        report_cels: Include per-frame cel details in output. Default False.
        report_bounds: Include bounding box info in overlap reports. Default False.
        max_overlaps: Maximum overlap entries to report. Default 200.
        max_out_of_range: Maximum out-of-range entries to report. Default 200.
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"

    err = check_file(filename)
    if err:
        return err

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    end_lua = str(end_frame) if end_frame is not None else "nil"

    # Build layer_names Lua table
    if layer_names:
        ln_entries = ", ".join('"' + _lua_escape(n) + '"' for n in layer_names)
        layer_names_lua = "{" + ln_entries + "}"
    else:
        layer_names_lua = "nil"

    overlap_pairs_lua = _parse_overlap_pairs(overlap_pairs)
    layer_frame_ranges_lua = _parse_layer_frame_ranges(layer_frame_ranges)

    report_cels_lua = "true" if report_cels else "false"
    report_bounds_lua = "true" if report_bounds else "false"

    script = (
        'local spr = app.open("' + escaped_filename + '")\n'
        'if not spr then return "Error: could not open sprite" end\n'
        "\n"
        "local start_idx = " + str(start_frame) + "\n"
        "local end_idx = " + end_lua + "\n"
        "if end_idx == nil then end_idx = #spr.frames end\n"
        "if start_idx < 1 then start_idx = 1 end\n"
        "if end_idx > #spr.frames then end_idx = #spr.frames end\n"
        "\n"
        "local layer_names_filter = " + layer_names_lua + "\n"
        "local overlap_pairs = " + overlap_pairs_lua + "\n"
        "local layer_frame_ranges = " + layer_frame_ranges_lua + "\n"
        "local report_cels = " + report_cels_lua + "\n"
        "local report_bounds = " + report_bounds_lua + "\n"
        "local max_overlaps = " + str(max_overlaps) + "\n"
        "local max_out_of_range = " + str(max_out_of_range) + "\n"
        "\n"
        "-- Collect layers to audit\n"
        "local all_layers = {}\n"
        "local layer_lookup = {}\n"
        "for _, layer in ipairs(spr.layers) do\n"
        "    layer_lookup[layer.name] = layer\n"
        "end\n"
        "\n"
        "if layer_names_filter then\n"
        "    for _, lname in ipairs(layer_names_filter) do\n"
        "        local layer = layer_lookup[lname]\n"
        "        if layer then\n"
        "            table.insert(all_layers, layer)\n"
        "        end\n"
        "    end\n"
        "else\n"
        "    for _, layer in ipairs(spr.layers) do\n"
        "        table.insert(all_layers, layer)\n"
        "    end\n"
        "end\n"
        "\n"
        "local total_cels = 0\n"
        "local cel_details = {}\n"
        "local overlap_entries = {}\n"
        "local out_of_range_entries = {}\n"
        "\n"
        "-- Iterate frames and collect cel data\n"
        "for fi = start_idx, end_idx do\n"
        "    local frame = spr.frames[fi]\n"
        "    local frame_info = { frame = fi, layers = {} }\n"
        "\n"
        "    for _, layer in ipairs(all_layers) do\n"
        "        local cel = layer:cel(frame)\n"
        "        if cel and cel.image then\n"
        "            total_cels = total_cels + 1\n"
        "            local info = { name = layer.name, "
        "x = cel.position.x, y = cel.position.y, "
        "w = cel.image.width, h = cel.image.height, "
        "opacity = cel.opacity }\n"
        "            table.insert(frame_info.layers, info)\n"
        "        end\n"
        "    end\n"
        "\n"
        "    if report_cels then\n"
        "        table.insert(cel_details, frame_info)\n"
        "    end\n"
        "end\n"
        "\n"
        "-- Check overlap pairs\n"
        "for _, pair in ipairs(overlap_pairs) do\n"
        "    local nameA = pair[1]\n"
        "    local nameB = pair[2]\n"
        "    local layerA = layer_lookup[nameA]\n"
        "    local layerB = layer_lookup[nameB]\n"
        "    if layerA and layerB then\n"
        "        for fi = start_idx, end_idx do\n"
        "            if #overlap_entries >= max_overlaps then break end\n"
        "            local frame = spr.frames[fi]\n"
        "            local celA = layerA:cel(frame)\n"
        "            local celB = layerB:cel(frame)\n"
        "            if celA and celB and celA.image and celB.image then\n"
        "                local ax1 = celA.position.x\n"
        "                local ay1 = celA.position.y\n"
        "                local ax2 = ax1 + celA.image.width\n"
        "                local ay2 = ay1 + celA.image.height\n"
        "                local bx1 = celB.position.x\n"
        "                local by1 = celB.position.y\n"
        "                local bx2 = bx1 + celB.image.width\n"
        "                local by2 = by1 + celB.image.height\n"
        "                local overlaps = not (ax2 <= bx1 "
        "or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)\n"
        "                if overlaps then\n"
        '                    local entry = \'{"frame":\' '
        '.. fi .. \',"layers":["\' .. nameA '
        '.. \'","\' .. nameB .. \'"]\'\n'
        "                    if report_bounds then\n"
        '                        entry = entry '
        '.. \',"boundsA":{"x":\' .. ax1 '
        '.. \',"y":\' .. ay1 .. \',"w":\' '
        '.. celA.image.width .. \',"h":\' '
        '.. celA.image.height .. \'}\'\n'
        '                        entry = entry '
        '.. \',"boundsB":{"x":\' .. bx1 '
        '.. \',"y":\' .. by1 .. \',"w":\' '
        '.. celB.image.width .. \',"h":\' '
        '.. celB.image.height .. \'}\'\n'
        "                    end\n"
        '                    entry = entry .. \'}\'\n'
        "                    table.insert(overlap_entries, entry)\n"
        "                end\n"
        "            end\n"
        "        end\n"
        "    end\n"
        "    if #overlap_entries >= max_overlaps then break end\n"
        "end\n"
        "\n"
        "-- Check out-of-range cels based on layer_frame_ranges\n"
        "if layer_frame_ranges and next(layer_frame_ranges) then\n"
        "    for layer_name, ranges in pairs(layer_frame_ranges) do\n"
        "        local layer = layer_lookup[layer_name]\n"
        "        if layer then\n"
        "            for fi = start_idx, end_idx do\n"
        "                if #out_of_range_entries >= max_out_of_range then break end\n"
        "                local frame = spr.frames[fi]\n"
        "                local cel = layer:cel(frame)\n"
        "                if cel and cel.image then\n"
        "                    local in_range = false\n"
        "                    for _, rng in ipairs(ranges) do\n"
        "                        if fi >= rng[1] and fi <= rng[2] then\n"
        "                            in_range = true\n"
        "                            break\n"
        "                        end\n"
        "                    end\n"
        "                    if not in_range then\n"
        '                        table.insert(out_of_range_entries, '
        '\'{"layer":"\' .. layer_name '
        '.. \'","frame":\' .. fi .. \'}\')\n'
        "                    end\n"
        "                end\n"
        "            end\n"
        "        end\n"
        "    end\n"
        "end\n"
        "\n"
        "-- Build JSON output\n"
        "local parts = {}\n"
        'table.insert(parts, \'{"frames":\' .. #spr.frames)\n'
        'table.insert(parts, \',"summary":{"total_layers":\' '
        '.. #spr.layers .. \',"layers_checked":\' '
        '.. #all_layers .. \',"total_cels":\' '
        '.. total_cels)\n'
        'table.insert(parts, \',"overlaps_count":\' '
        '.. #overlap_entries '
        '.. \',"out_of_range_count":\' '
        '.. #out_of_range_entries .. \'}\')\n'
        "\n"
        "-- overlaps\n"
        'table.insert(parts, \',"overlaps\":[\' '
        '.. table.concat(overlap_entries, \",\") .. \']\')\n'
        "\n"
        "-- out_of_range\n"
        'table.insert(parts, \',"out_of_range\":[\' '
        '.. table.concat(out_of_range_entries, \",\") '
        '.. \']\')\n'
        "\n"
        "-- cel_details (optional)\n"
        "if report_cels then\n"
        "    local cd_parts = {}\n"
        "    for _, fi in ipairs(cel_details) do\n"
        "        local layer_parts = {}\n"
        "        for j, li in ipairs(fi.layers) do\n"
        '            layer_parts[j] = \'{"name":"\' '
        '.. li.name .. \'","x":\' .. li.x '
        '.. \',"y":\' .. li.y .. \',"w":\' '
        '.. li.w .. \',"h":\' .. li.h '
        '.. \',"opacity":\' .. li.opacity .. \'}\'\n'
        "        end\n"
        '        cd_parts[#cd_parts + 1] = \'{"frame":\' '
        '.. fi.frame .. \',"layers\":[\' '
        '.. table.concat(layer_parts, \",\") '
        '.. \']}\'\n'
        "    end\n"
        '    table.insert(parts, \',"cel_details\":[\' '
        '.. table.concat(cd_parts, \",\") .. \']\')\n'
        "end\n"
        "\n"
        'table.insert(parts, \'}\')\n'
        "\n"
        "spr:close()\n"
        "\n"
        'print("JSON_START" .. table.concat(parts))\n'
    )

    success, output = get_cli().execute_lua_script(script)
    if success:
        return output.strip()
    return "Failed to audit animation: " + output


# ---------------------------------------------------------------------------
# Tool: animation_sanitize
# ---------------------------------------------------------------------------


@mcp.tool()
async def animation_sanitize(
    filename: str,
    start_frame: int = 1,
    end_frame: int | None = None,
    layer_names: list[str] | None = None,
    layer_order: list[str] | None = None,
    layer_frame_ranges: list[str] | None = None,
    ensure_layers: list[str] | None = None,
    overlap_pairs: list[str] | None = None,
    report_bounds: bool = False,
    max_overlaps: int = 200,
    ignore_full_canvas_overlaps: bool = True,
    out_of_range_action: str = "set_opacity_zero",
    out_of_range_opacity: int = 0,
    report_only: bool = False,
    include_stats: bool = True,
) -> str:
    """Validate and optionally fix animation consistency issues.

    Normalises animation by reordering layers, creating missing cels, and
    handling out-of-range cels. Returns detailed JSON analysis.

    Args:
        filename: Path to the Aseprite file.
        start_frame: First frame (1-based, inclusive). Default 1.
        end_frame: Last frame (1-based, inclusive). None = last frame.
        layer_names: Only process these layers. None = all layers.
        layer_order: Reorder layers to match this name order (bottom-to-top).
        layer_frame_ranges: Expected frame ranges per layer, e.g. ["clouds:1-12"].
        ensure_layers: Create missing cels for these layers across the frame range.
        overlap_pairs: Layer pairs to check for overlaps, e.g. ["layerA,layerB"].
        report_bounds: Include bounding box info in overlap reports. Default False.
        max_overlaps: Maximum overlap entries to report. Default 200.
        ignore_full_canvas_overlaps: Skip overlaps where either cel
            covers the full canvas. Default True.
        out_of_range_action: Action for out-of-range cels:
            "set_opacity_zero", "delete_cels", or "none".
            Default "set_opacity_zero".
        out_of_range_opacity: Opacity value for "set_opacity_zero" action. Default 0.
        report_only: If True, only report issues without making changes. Default False.
        include_stats: Include per-layer statistics in output. Default True.
    """
    if ".." in filename:
        return "Error: filename must not contain '..' (path traversal)"

    err = check_file(filename)
    if err:
        return err

    # Validate out_of_range_action
    valid_actions = {"set_opacity_zero", "delete_cels", "none"}
    if out_of_range_action not in valid_actions:
        return (
            "Error: out_of_range_action must be one of "
            + str(sorted(valid_actions))
            + ", got '"
            + out_of_range_action
            + "'"
        )

    escaped_filename = _lua_escape(filename.replace("\\", "/"))
    end_lua = str(end_frame) if end_frame is not None else "nil"

    # Build layer_names Lua table
    if layer_names:
        ln_entries = ", ".join('"' + _lua_escape(n) + '"' for n in layer_names)
        layer_names_lua = "{" + ln_entries + "}"
    else:
        layer_names_lua = "nil"

    # Build layer_order Lua table
    if layer_order:
        lo_entries = ", ".join('"' + _lua_escape(n) + '"' for n in layer_order)
        layer_order_lua = "{" + lo_entries + "}"
    else:
        layer_order_lua = "nil"

    # Build ensure_layers Lua table
    if ensure_layers:
        el_entries = ", ".join('"' + _lua_escape(n) + '"' for n in ensure_layers)
        ensure_layers_lua = "{" + el_entries + "}"
    else:
        ensure_layers_lua = "nil"

    overlap_pairs_lua = _parse_overlap_pairs(overlap_pairs)
    layer_frame_ranges_lua = _parse_layer_frame_ranges(layer_frame_ranges)

    report_bounds_lua = "true" if report_bounds else "false"
    ignore_full_lua = "true" if ignore_full_canvas_overlaps else "false"
    report_only_lua = "true" if report_only else "false"
    include_stats_lua = "true" if include_stats else "false"

    # Map action string to Lua string literal
    action_map = {
        "set_opacity_zero": '"set_opacity_zero"',
        "delete_cels": '"delete_cels"',
        "none": '"none"',
    }
    out_of_range_action_lua = action_map[out_of_range_action]

    script = (
        'local spr = app.open("' + escaped_filename + '")\n'
        'if not spr then return "Error: could not open sprite" end\n'
        "\n"
        "local start_idx = " + str(start_frame) + "\n"
        "local end_idx = " + end_lua + "\n"
        "if end_idx == nil then end_idx = #spr.frames end\n"
        "if start_idx < 1 then start_idx = 1 end\n"
        "if end_idx > #spr.frames then end_idx = #spr.frames end\n"
        "\n"
        "local layer_names_filter = " + layer_names_lua + "\n"
        "local layer_order = " + layer_order_lua + "\n"
        "local ensure_layer_names = " + ensure_layers_lua + "\n"
        "local overlap_pairs = " + overlap_pairs_lua + "\n"
        "local layer_frame_ranges = " + layer_frame_ranges_lua + "\n"
        "local report_bounds = " + report_bounds_lua + "\n"
        "local ignore_full_canvas_overlaps = " + ignore_full_lua + "\n"
        "local out_of_range_action = " + out_of_range_action_lua + "\n"
        "local out_of_range_opacity = " + str(out_of_range_opacity) + "\n"
        "local report_only = " + report_only_lua + "\n"
        "local include_stats = " + include_stats_lua + "\n"
        "local max_overlaps = " + str(max_overlaps) + "\n"
        "\n"
        "local changed = false\n"
        "local alerts = {}\n"
        "\n"
        "-- Build layer lookup\n"
        "local layer_lookup = {}\n"
        "for _, layer in ipairs(spr.layers) do\n"
        "    layer_lookup[layer.name] = layer\n"
        "end\n"
        "\n"
        "-- Collect layers to process\n"
        "local process_layers = {}\n"
        "if layer_names_filter then\n"
        "    for _, lname in ipairs(layer_names_filter) do\n"
        "        local layer = layer_lookup[lname]\n"
        "        if layer then\n"
        "            table.insert(process_layers, layer)\n"
        "        end\n"
        "    end\n"
        "else\n"
        "    for _, layer in ipairs(spr.layers) do\n"
        "        table.insert(process_layers, layer)\n"
        "    end\n"
        "end\n"
        "\n"
        "-- Step 1: Reorder layers\n"
        "if layer_order then\n"
        "    local reorder_ok = true\n"
        "    for _, name in ipairs(layer_order) do\n"
        "        if not layer_lookup[name] then\n"
        '            table.insert(alerts, '
        '\'Layer "\' .. name .. \'" not found for reordering\')\n'
        "            reorder_ok = false\n"
        "        end\n"
        "    end\n"
        "    if reorder_ok then\n"
        "        for i, name in ipairs(layer_order) do\n"
        "            local layer = layer_lookup[name]\n"
        "            layer.stackIndex = i\n"
        "        end\n"
        "        changed = true\n"
        '        table.insert(alerts, "Reordered layers to match specified order")\n'
        "        -- Refresh lookup after reorder\n"
        "        layer_lookup = {}\n"
        "        for _, layer in ipairs(spr.layers) do\n"
        "            layer_lookup[layer.name] = layer\n"
        "        end\n"
        "    end\n"
        "end\n"
        "\n"
        "-- Step 2: Ensure layers have cels\n"
        "if ensure_layer_names then\n"
        "    local created_count = 0\n"
        "    app.transaction(function()\n"
        "        for _, lname in ipairs(ensure_layer_names) do\n"
        "            local layer = layer_lookup[lname]\n"
        "            if not layer then\n"
        '                table.insert(alerts, '
        '\'Layer "\' .. lname '
        '.. \'" not found for ensuring cels\')\n'
        "                goto continue_ensure\n"
        "            end\n"
        "            for fi = start_idx, end_idx do\n"
        "                local frame = spr.frames[fi]\n"
        "                local cel = layer:cel(frame)\n"
        "                if not cel then\n"
        "                    local img = Image(spr.width, spr.height, spr.colorMode)\n"
        "                    spr:newCel(layer, frame, img, Point(0, 0))\n"
        "                    created_count = created_count + 1\n"
        "                end\n"
        "            end\n"
        "            ::continue_ensure::\n"
        "        end\n"
        "    end)\n"
        "    if created_count > 0 then\n"
        "        changed = true\n"
        '        table.insert(alerts, '
        '"Created " .. created_count .. " missing cel(s)")\n'
        "    end\n"
        "end\n"
        "\n"
        "-- Step 3: Handle out-of-range cels\n"
        "local out_of_range_entries = {}\n"
        "local oor_deleted = 0\n"
        "local oor_opacity_changed = 0\n"
        "\n"
        "if layer_frame_ranges and next(layer_frame_ranges) then\n"
        "    for layer_name, ranges in pairs(layer_frame_ranges) do\n"
        "        local layer = layer_lookup[layer_name]\n"
        "        if layer then\n"
        "            for fi = start_idx, end_idx do\n"
        "                local frame = spr.frames[fi]\n"
        "                local cel = layer:cel(frame)\n"
        "                if cel and cel.image then\n"
        "                    local in_range = false\n"
        "                    for _, rng in ipairs(ranges) do\n"
        "                        if fi >= rng[1] and fi <= rng[2] then\n"
        "                            in_range = true\n"
        "                            break\n"
        "                        end\n"
        "                    end\n"
        "                    if not in_range then\n"
        '                        local entry = \'{"layer":"\' '
        '.. layer_name .. \'","frame":\' '
        '.. fi .. \'}\'\n'
        "                        table.insert("
        "out_of_range_entries, entry)\n"
        "\n"
        "                        if not report_only then\n"
        '                            if out_of_range_action == "delete_cels" then\n'
        "                                spr:deleteCel(cel)\n"
        "                                oor_deleted = oor_deleted + 1\n"
        "                                changed = true\n"
        '                            elseif '
        'out_of_range_action == "set_opacity_zero" '
        'then\n'
        "                                cel.opacity = out_of_range_opacity\n"
        "                                "
        "oor_opacity_changed = "
        "oor_opacity_changed + 1\n"
        "                                changed = true\n"
        "                            end\n"
        "                        end\n"
        "                    end\n"
        "                end\n"
        "            end\n"
        "        end\n"
        "    end\n"
        "end\n"
        "\n"
        "if oor_deleted > 0 then\n"
        '    table.insert(alerts, '
        '"Deleted " .. oor_deleted '
        '.. " out-of-range cel(s)")\n'
        "end\n"
        "if oor_opacity_changed > 0 then\n"
        '    table.insert(alerts, '
        '"Set opacity on " .. oor_opacity_changed '
        '.. " out-of-range cel(s)")\n'
        "end\n"
        "\n"
        "-- Step 4: Check overlaps\n"
        "local overlap_entries = {}\n"
        "\n"
        "for _, pair in ipairs(overlap_pairs) do\n"
        "    local nameA = pair[1]\n"
        "    local nameB = pair[2]\n"
        "    local layerA = layer_lookup[nameA]\n"
        "    local layerB = layer_lookup[nameB]\n"
        "    if layerA and layerB then\n"
        "        for fi = start_idx, end_idx do\n"
        "            if #overlap_entries >= max_overlaps then break end\n"
        "            local frame = spr.frames[fi]\n"
        "            local celA = layerA:cel(frame)\n"
        "            local celB = layerB:cel(frame)\n"
        "            if celA and celB and celA.image and celB.image then\n"
        "                local ax1 = celA.position.x\n"
        "                local ay1 = celA.position.y\n"
        "                local ax2 = ax1 + celA.image.width\n"
        "                local ay2 = ay1 + celA.image.height\n"
        "                local bx1 = celB.position.x\n"
        "                local by1 = celB.position.y\n"
        "                local bx2 = bx1 + celB.image.width\n"
        "                local by2 = by1 + celB.image.height\n"
        "\n"
        "                -- Skip full-canvas overlaps if requested\n"
        "                if ignore_full_canvas_overlaps then\n"
        "                    local a_full = ("
        "celA.image.width >= spr.width "
        "and celA.image.height >= spr.height\n"
        "                        and celA.position.x <= 0 "
        "and celA.position.y <= 0)\n"
        "                    local b_full = ("
        "celB.image.width >= spr.width "
        "and celB.image.height >= spr.height\n"
        "                        and celB.position.x <= 0 "
        "and celB.position.y <= 0)\n"
        "                    if a_full or b_full then\n"
        "                        goto continue_overlap\n"
        "                    end\n"
        "                end\n"
        "\n"
        "                local overlaps = not (ax2 <= bx1 "
        "or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)\n"
        "                if overlaps then\n"
        '                    local entry = \'{"frame":\' '
        '.. fi .. \',"layers":["\' .. nameA '
        '.. \'","\' .. nameB .. \'"]\'\n'
        "                    if report_bounds then\n"
        '                        entry = entry '
        '.. \',"boundsA":{"x":\' .. ax1 '
        '.. \',"y":\' .. ay1 .. \',"w":\' '
        '.. celA.image.width .. \',"h":\' '
        '.. celA.image.height .. \'}\'\n'
        '                        entry = entry '
        '.. \',"boundsB":{"x":\' .. bx1 '
        '.. \',"y":\' .. by1 .. \',"w":\' '
        '.. celB.image.width .. \',"h":\' '
        '.. celB.image.height .. \'}\'\n'
        "                    end\n"
        '                    entry = entry .. \'}\'\n'
        "                    table.insert(overlap_entries, entry)\n"
        "                end\n"
        "            end\n"
        "            ::continue_overlap::\n"
        "        end\n"
        "    end\n"
        "    if #overlap_entries >= max_overlaps then break end\n"
        "end\n"
        "\n"
        "-- Step 5: Collect stats\n"
        "local total_cels = 0\n"
        "local layer_stats_parts = {}\n"
        "for _, layer in ipairs(process_layers) do\n"
        "    local layer_cel_count = 0\n"
        "    for fi = start_idx, end_idx do\n"
        "        local cel = layer:cel(spr.frames[fi])\n"
        "        if cel and cel.image then\n"
        "            layer_cel_count = layer_cel_count + 1\n"
        "            total_cels = total_cels + 1\n"
        "        end\n"
        "    end\n"
        "    if include_stats then\n"
        '        layer_stats_parts[#layer_stats_parts + 1] = '
        '\'{"name":"\' .. layer.name '
        '.. \'","cels":\' .. layer_cel_count .. \'}\'\n'
        "    end\n"
        "end\n"
        "\n"
        "-- Save if changed and not report_only\n"
        "if changed and not report_only then\n"
        "    spr:saveAs(spr.filename)\n"
        "end\n"
        "\n"
        "-- Build JSON output\n"
        "local parts = {}\n"
        'local sanitized_val = (not report_only and changed) and "true" or "false"\n'
        'table.insert(parts, \'{"sanitized":\' .. sanitized_val)\n'
        "\n"
        'table.insert(parts, \',"analysis":{"total_layers":\' '
        '.. #spr.layers '
        '.. \',"layers_checked":\' '
        '.. #process_layers '
        '.. \',"total_cels":\' .. total_cels '
        '.. \',"overlaps_found":\' '
        '.. #overlap_entries '
        '.. \',"out_of_range_found":\' '
        '.. #out_of_range_entries .. \'}\')\n'
        "\n"
        "if include_stats then\n"
        '    table.insert(parts, \',"layer_stats\":[\' '
        '.. table.concat(layer_stats_parts, \",\") '
        '.. \']\')\n'
        "end\n"
        "\n"
        'table.insert(parts, \',"overlaps\":[\' '
        '.. table.concat(overlap_entries, \",\") '
        '.. \']\')\n'
        'table.insert(parts, \',"out_of_range\":[\' '
        '.. table.concat(out_of_range_entries, \",\") '
        '.. \']\')\n'
        "\n"
        "-- alerts\n"
        "local alert_parts = {}\n"
        "for i, alert in ipairs(alerts) do\n"
        '    alert_parts[i] = \'"\' .. alert:gsub(\'"\', \'\\\\"\') .. \'"\'\n'
        "end\n"
        'table.insert(parts, \',"alerts\":[\' '
        '.. table.concat(alert_parts, \",\") .. \']\')\n'
        "\n"
        'table.insert(parts, \'}\')\n'
        "\n"
        "spr:close()\n"
        "\n"
        'print("JSON_START" .. table.concat(parts))\n'
    )

    success, output = get_cli().execute_lua_script(script)
    if success:
        return output.strip()
    return "Failed to sanitize animation: " + output
