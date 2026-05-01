"""Aseprite MCP Server - FastMCP server with tools, resources, and prompts."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

# Import tools package to register all tool modules on the MCP server.
# Each submodule uses @mcp.tool() decorators that register themselves on import.
import aseprite_mcp.tools  # noqa: F401
from aseprite_mcp import mcp
from aseprite_mcp.aseprite_cli import AsepriteCLI, AsepriteCLIError
from aseprite_mcp.config import AsepriteConfig
from aseprite_mcp.lua_scripts import (
    create_sprite_script,
    export_sprite_script,
    sprite_info_script,
)
from aseprite_mcp.utils import (
    validate_color_mode,
    validate_dimensions,
    validate_sprite_path,
)
from aseprite_mcp.websocket_bridge import WebSocketBridge

logger = logging.getLogger(__name__)

_config: AsepriteConfig | None = None
_cli: AsepriteCLI | None = None
_ws_bridge: WebSocketBridge | None = None


def _get_config() -> AsepriteConfig:
    global _config
    if _config is None:
        _config = AsepriteConfig.from_env()
    return _config


def _get_cli() -> AsepriteCLI:
    global _cli
    if _cli is None:
        _cli = AsepriteCLI(_get_config())
    return _cli


def _get_ws_bridge() -> WebSocketBridge:
    global _ws_bridge
    if _ws_bridge is None:
        _ws_bridge = WebSocketBridge(_get_config())
    return _ws_bridge


# ── Tools ────────────────────────────────────────────────────────────────


@mcp.tool()
async def sprite_create(
    width: int, height: int, color_mode: str = "rgb", output_path: str = ""
) -> str:
    """Create a new Aseprite sprite with the given dimensions.

    Args:
        width: Sprite width in pixels (1-4096)
        height: Sprite height in pixels (1-4096)
        color_mode: Color mode - "rgb", "grayscale", or "indexed"
        output_path: Path to save the sprite (.ase). If empty, saves to output_dir.
    """
    try:
        validate_dimensions(width, height)
        validate_color_mode(color_mode)
    except ValueError as e:
        return f"Error: {e}"

    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sprite_{width}x{height}_{color_mode}_{timestamp}.ase"
        output_path = str(_get_config().resolve_output_path(filename))

    script = create_sprite_script(width, height, color_mode, output_path)
    params: dict[str, str] = {"output": output_path}

    try:
        result = _get_cli().run_json_script(script, params)
        return json.dumps(result)
    except AsepriteCLIError as e:
        return f"Error: {e}"
    except ValueError as e:
        return f"Error: {e}"


@mcp.tool()
async def sprite_export(
    input_path: str, output_path: str = ""
) -> str:
    """Export a sprite to another format (PNG, GIF, etc.).

    Args:
        input_path: Path to the source sprite file
        output_path: Path for the exported file (extension determines format).
            If empty, saves to output_dir with PNG format.
    """
    try:
        validate_sprite_path(input_path)
    except ValueError as e:
        return f"Error: {e}"

    if not output_path:
        stem = Path(input_path).stem
        filename = f"{stem}.png"
        output_path = str(_get_config().resolve_output_path(filename))

    script = export_sprite_script(input_path, output_path)

    try:
        result = _get_cli().run_json_script(script)
        return json.dumps(result)
    except AsepriteCLIError as e:
        return f"Error: {e}"


@mcp.tool()
async def sprite_info(file_path: str) -> str:
    """Get metadata about a sprite (dimensions, layers, tags, frames, palette).

    Args:
        file_path: Path to the sprite file
    """
    try:
        validate_sprite_path(file_path)
    except ValueError as e:
        return f"Error: {e}"
    script = sprite_info_script(file_path)

    try:
        result = _get_cli().run_json_script(script)
        return json.dumps(result, indent=2)
    except AsepriteCLIError as e:
        return f"Error: {e}"


@mcp.tool()
async def sprite_list_layers(file_path: str) -> str:
    """List all layers in a sprite file.

    Args:
        file_path: Path to the sprite file
    """
    try:
        layers = _get_cli().list_layers(file_path)
        return json.dumps({"layers": layers})
    except AsepriteCLIError as e:
        return f"Error: {e}"


@mcp.tool()
async def sprite_list_tags(file_path: str) -> str:
    """List all frame tags in a sprite file.

    Args:
        file_path: Path to the sprite file
    """
    try:
        tags = _get_cli().list_tags(file_path)
        return json.dumps({"tags": tags})
    except AsepriteCLIError as e:
        return f"Error: {e}"


@mcp.tool()
async def spritesheet_export(
    input_path: str,
    sheet_path: str = "",
    data_path: str = "",
    sheet_type: str = "packed",
    border_padding: int = 0,
    shape_padding: int = 0,
    inner_padding: int = 0,
    trim: bool = False,
) -> str:
    """Export a sprite as a spritesheet with optional JSON metadata.

    Args:
        input_path: Path to the sprite file
        sheet_path: Output PNG path for the spritesheet.
            If empty, saves to output_dir.
        data_path: Output JSON path for atlas metadata.
            If empty, saves to output_dir.
        sheet_type: Layout algorithm - "horizontal", "vertical",
            "rows", "columns", "packed"
        border_padding: Padding on texture borders
        shape_padding: Padding between frames
        inner_padding: Padding inside each frame
        trim: Trim individual frames
    """
    stem = Path(input_path).stem
    config = _get_config()

    if not sheet_path:
        sheet_path = str(config.resolve_output_path(f"{stem}_sheet.png"))
    if not data_path:
        data_path = str(config.resolve_output_path(f"{stem}_atlas.json"))

    args = [
        "--sheet", sheet_path,
        "--data", data_path,
        "--sheet-type", sheet_type,
        "--border-padding", str(border_padding),
        "--shape-padding", str(shape_padding),
        "--inner-padding", str(inner_padding),
    ]
    if trim:
        args.append("--trim")

    args.append(input_path)

    try:
        result = _get_cli().run_batch(args)
        if result.returncode != 0:
            return f"Error: {result.stderr.decode(errors='replace')}"
        return json.dumps({
            "sheet": sheet_path,
            "data": data_path,
            "success": True,
        })
    except AsepriteCLIError as e:
        return f"Error: {e}"


@mcp.tool()
async def script_execute(
    lua_code: str, params: dict[str, str] | None = None
) -> str:
    """Execute a custom Lua script in Aseprite batch mode.

    Args:
        lua_code: Lua script code to execute
        params: Optional key-value parameters accessible via app.params
    """
    try:
        result = _get_cli().run_script(lua_code, params)
        return result
    except AsepriteCLIError as e:
        return f"Error: {e}"


@mcp.tool()
async def ws_connect(sprite_path: str = "") -> str:
    """Launch Aseprite with WebSocket bridge for real-time drawing.

    Opens Aseprite GUI with a Lua script that connects back to the MCP
    server's WebSocket endpoint, enabling interactive pixel manipulation.

    Args:
        sprite_path: Optional path to a sprite file to open
    """
    bridge = _get_ws_bridge()

    try:
        await bridge.start()
        path = sprite_path if sprite_path else None
        bridge.launch_aseprite_with_bridge(path)
        return json.dumps({
            "status": "launched",
            "ws_url": bridge.ws_url,
            "sprite": sprite_path or "new",
        })
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def ws_draw_pixels(pixels: list[dict[str, Any]]) -> str:
    """Draw pixels on the active sprite via WebSocket (real-time mode).

    Requires ws_connect to be called first. For file-based pixel
    drawing, use draw_pixels instead.

    Each pixel is a dict with keys: x (int), y (int), color (hex string like "#ff0000").

    Args:
        pixels: List of pixel dicts, e.g. [{"x": 10, "y": 5, "color": "#ff0000"}]
    """
    bridge = _get_ws_bridge()
    command = {"action": "draw_pixels", "pixels": pixels}

    try:
        result = await bridge.send_command(command)
        return json.dumps(result)
    except ConnectionError as e:
        return f"Error: No WebSocket connection. Use ws_connect first. ({e})"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def ws_fill_rect(
    x: int, y: int, width: int, height: int, color: str
) -> str:
    """Fill a rectangular area on the active sprite via WebSocket
    (real-time mode).

    Requires ws_connect to be called first. For file-based rectangle
    fill, use fill_rect or draw_rectangle instead.

    Args:
        x: X position of the rectangle
        y: Y position of the rectangle
        width: Width of the rectangle
        height: Height of the rectangle
        color: Hex color string (e.g., "#ff0000")
    """
    bridge = _get_ws_bridge()
    command = {
        "action": "fill_rect",
        "x": x,
        "y": y,
        "w": width,
        "h": height,
        "color": color,
    }

    try:
        result = await bridge.send_command(command)
        return json.dumps(result)
    except ConnectionError as e:
        return f"Error: No WebSocket connection. Use ws_connect first. ({e})"
    except Exception as e:
        return f"Error: {e}"


# ── Resources ────────────────────────────────────────────────────────────


@mcp.resource("aseprite://sprites/{path}")
def get_sprite_resource(path: str) -> str:
    """Get sprite metadata as a resource."""
    try:
        script = sprite_info_script(path)
        result = _get_cli().run_json_script(script)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("aseprite://palettes/{name}")
def get_palette_resource(name: str) -> str:
    """Get built-in palette data."""
    palettes = {
        "dawnbringer32": [
            "#000000", "#222034", "#45283c", "#663931",
            "#8f563b", "#df7126", "#d9a066", "#eec39a",
            "#fbf236", "#99e550", "#6abe30", "#37946e",
            "#4b692f", "#524b24", "#323c39", "#3f3f74",
        ],
        "pico8": [
            "#000000", "#1d2b53", "#7e2553", "#008751",
            "#ab5236", "#5f574f", "#c2c3c7", "#fff1e8",
            "#ff004d", "#ffa300", "#ffec27", "#00e436",
            "#29adff", "#83769c", "#ff77a8", "#ffccaa",
        ],
    }
    if name.lower() in palettes:
        return json.dumps({
            "name": name,
            "colors": palettes[name.lower()],
        })
    return json.dumps({
        "error": f"Palette '{name}' not found",
        "available": list(palettes.keys()),
    })


# ── Prompts ──────────────────────────────────────────────────────────────


@mcp.prompt()
def pixel_art_asset_gen(
    asset_type: str = "character",
    size: str = "16x16",
) -> str:
    """Template for generating pixel art assets with LLM guidance."""
    return (
        f"You are a pixel art asset generator. "
        f"Use the Aseprite MCP tools to create a pixel art {asset_type}.\n"
        "\n"
        "Guidelines:\n"
        f"1. Use sprite_create to establish a {size} canvas\n"
        "2. Plan the silhouette first, then add detail and color\n"
        "3. Use a limited palette (4-8 colors) for authentic pixel art\n"
        "4. Use draw_pixels or fill_rect to place pixels strategically\n"
        "5. Use sprite_export to save as PNG when complete\n"
        "\n"
        f"For the {asset_type}:\n"
        "- Start with the overall shape/silhouette\n"
        "- Add defining features that make it recognizable\n"
        "- Use shading (light, mid, dark) for depth\n"
        f"- Keep within {size} resolution - every pixel counts\n"
        "\n"
        "Available tools: sprite_create, sprite_export, "
        "sprite_info, ws_draw_pixels, ws_fill_rect, ws_connect, "
        "and all drawing/animation tools\n"
    )


def run_server(
    transport: Literal["stdio", "sse", "streamable-http"] = "stdio",
    port: int = 8080,
) -> None:
    if transport == "streamable-http":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = port
    mcp.run(transport=transport)
