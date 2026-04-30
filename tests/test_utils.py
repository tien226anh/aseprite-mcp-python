"""Tests for aseprite_mcp.utils module."""

from __future__ import annotations

import pytest

from aseprite_mcp.utils import (
    parse_hex_color,
    rgba_to_hex,
    validate_color_mode,
    validate_dimensions,
    validate_sprite_path,
)


class TestParseHexColor:
    def test_full_hex(self) -> None:
        assert parse_hex_color("#ff0000") == (255, 0, 0, 255)

    def test_hex_no_hash(self) -> None:
        assert parse_hex_color("ff0000") == (255, 0, 0, 255)

    def test_hex_with_alpha(self) -> None:
        assert parse_hex_color("#ff000080") == (255, 0, 0, 128)

    def test_uppercase(self) -> None:
        assert parse_hex_color("#FF0000") == (255, 0, 0, 255)

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid hex color"):
            parse_hex_color("not_a_color")

    def test_invalid_short(self) -> None:
        with pytest.raises(ValueError, match="Invalid hex color"):
            parse_hex_color("#fff")

    def test_black(self) -> None:
        assert parse_hex_color("#000000") == (0, 0, 0, 255)

    def test_white(self) -> None:
        assert parse_hex_color("#ffffff") == (255, 255, 255, 255)


class TestRgbaToHex:
    def test_rgb(self) -> None:
        assert rgba_to_hex(255, 0, 0) == "#ff0000ff"

    def test_with_alpha(self) -> None:
        assert rgba_to_hex(255, 0, 0, 128) == "#ff000080"


class TestValidateDimensions:
    def test_valid_dimensions(self) -> None:
        validate_dimensions(1, 1)
        validate_dimensions(4096, 4096)
        validate_dimensions(32, 32)

    def test_zero_width_raises(self) -> None:
        with pytest.raises(ValueError, match="Width"):
            validate_dimensions(0, 32)

    def test_too_large_raises(self) -> None:
        with pytest.raises(ValueError, match="Width"):
            validate_dimensions(4097, 32)

    def test_zero_height_raises(self) -> None:
        with pytest.raises(ValueError, match="Height"):
            validate_dimensions(32, 0)


class TestValidateColorMode:
    def test_valid_modes(self) -> None:
        validate_color_mode("rgb")
        validate_color_mode("grayscale")
        validate_color_mode("indexed")
        validate_color_mode("RGB")
        validate_color_mode("Grayscale")

    def test_invalid_mode_raises(self) -> None:
        with pytest.raises(ValueError, match="Color mode"):
            validate_color_mode("cmyk")


class TestValidateSpritePath:
    def test_valid_extensions(self) -> None:
        for ext in [".ase", ".aseprite", ".png", ".gif", ".jpg", ".bmp", ".webp"]:
            validate_sprite_path(f"test{ext}")

    def test_invalid_extension_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported sprite format"):
            validate_sprite_path("test.pdf")
