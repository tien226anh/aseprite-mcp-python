"""Export tools for Aseprite MCP — spritesheets and format conversion."""

from __future__ import annotations

import os

from aseprite_mcp import mcp
from aseprite_mcp.tools._helpers import _lua_escape, check_file, get_cli


@mcp.tool()
async def export_sprite(
    filename: str, output_filename: str, format: str = "png"
) -> str:
    """Export a sprite to another format (PNG, GIF, etc.).

    Args:
        filename: Path to the source Aseprite file
        output_filename: Path for the exported file
        format: Output format (png, gif, jpg, bmp, webp). Default: png
    """
    err = check_file(filename)
    if err:
        return err

    fmt = format.lower()
    valid_formats = {"png", "gif", "jpg", "jpeg", "bmp", "webp", "aseprite", "ase"}
    if fmt not in valid_formats:
        return (
            f"Error: unsupported format '{format}'. "
            f"Valid: {', '.join(sorted(valid_formats))}"
        )

    # Use Aseprite CLI --save-as for format conversion
    try:
        result = get_cli().run_batch(
            args=["--batch", filename, "--save-as", output_filename]
        )
        if result.returncode == 0:
            return f"Exported '{filename}' to '{output_filename}'"
        return f"Failed to export sprite: {result.stderr.decode(errors='replace')}"
    except Exception as e:
        return f"Failed to export sprite: {e}"


@mcp.tool()
async def copy_sprite(
    filename: str, output_filename: str, overwrite: bool = False
) -> str:
    """Copy a sprite to a new .aseprite file.

    Args:
        filename: Path to the source Aseprite file
        output_filename: Path for the copied file (must end in .aseprite)
        overwrite: If True, overwrite existing output file. Default: False
    """
    err = check_file(filename)
    if err:
        return err

    if not overwrite and os.path.exists(output_filename):
        return (
            f"Error: output file '{output_filename}' already exists. "
            f"Set overwrite=True to replace it."
        )

    if not output_filename.lower().endswith((".aseprite", ".ase")):
        return "Error: output_filename must end in .aseprite or .ase"

    escaped_output = _lua_escape(output_filename.replace("\\", "/"))

    script = f"""
local spr = app.activeSprite
if not spr then return "No active sprite" end

spr:saveAs("{escaped_output}")
return "Sprite copied"
"""

    success, output = get_cli().execute_lua_script(script, filename)
    if success:
        return f"Copied '{filename}' to '{output_filename}'"
    return f"Failed to copy sprite: {output}"
