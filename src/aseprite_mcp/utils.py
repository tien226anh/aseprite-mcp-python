"""Utility helpers for Aseprite MCP server."""

from __future__ import annotations

import re


def parse_hex_color(color: str) -> tuple[int, int, int, int]:
    hex_pattern = re.compile(
        r"^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})(?:([0-9a-fA-F]{2}))?$"
    )
    m = hex_pattern.match(color.strip())
    if not m:
        raise ValueError(f"Invalid hex color: {color}")
    r = int(m.group(1), 16)
    g = int(m.group(2), 16)
    b = int(m.group(3), 16)
    a = int(m.group(4), 16) if m.group(4) else 255
    return (r, g, b, a)


def rgba_to_hex(r: int, g: int, b: int, a: int = 255) -> str:
    return f"#{r:02x}{g:02x}{b:02x}{a:02x}"


def validate_dimensions(width: int, height: int) -> None:
    if not (1 <= width <= 4096):
        raise ValueError(f"Width must be between 1 and 4096, got {width}")
    if not (1 <= height <= 4096):
        raise ValueError(f"Height must be between 1 and 4096, got {height}")


def validate_color_mode(mode: str) -> None:
    valid = {"rgb", "grayscale", "indexed"}
    if mode.lower() not in valid:
        raise ValueError(f"Color mode must be one of {valid}, got {mode}")


def validate_sprite_path(path: str) -> None:
    exts = {".ase", ".aseprite", ".png", ".gif", ".jpg", ".jpeg", ".bmp", ".webp"}
    from pathlib import Path

    p = Path(path)
    if p.suffix.lower() not in exts:
        raise ValueError(
            f"Unsupported sprite format: {p.suffix}. "
            f"Supported: {sorted(exts)}"
        )
