"""Shared helpers for Aseprite MCP tool modules."""

from __future__ import annotations

import os

from aseprite_mcp.aseprite_cli import AsepriteCLI
from aseprite_mcp.config import AsepriteConfig


def get_cli() -> AsepriteCLI:
    """Get the AsepriteCLI singleton from the server module."""
    from aseprite_mcp.server import _get_cli

    return _get_cli()


def get_config() -> AsepriteConfig:
    """Get the AsepriteConfig singleton from the server module."""
    from aseprite_mcp.server import _get_config

    return _get_config()


def check_file(filename: str) -> str | None:
    """Check if a file exists. Returns error message if not found, None if OK."""
    if not os.path.exists(filename):
        return f"File {filename} not found"
    return None


def _lua_escape(s: str) -> str:
    """Escape a string for safe embedding inside a Lua double-quoted string literal."""
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\0", "\\0")
    )


def validate_hex_color(color: str) -> tuple[int, int, int] | None:
    """Parse a hex color string (#RRGGBB) to (r, g, b) tuple.
    Returns None if invalid."""
    if not color:
        return None
    hex_color = color.lstrip("#")
    if len(hex_color) != 6:
        return None
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        return None
    return r, g, b
