"""Tests for aseprite_mcp.tools._helpers module."""

from __future__ import annotations

import os
import tempfile

import pytest

from aseprite_mcp.tools._helpers import check_file, validate_hex_color


class TestCheckFile:
    def test_check_file_exists(self, tmp_path):
        """check_file returns None for existing file."""
        f = tmp_path / "test.ase"
        f.write_text("dummy")
        result = check_file(str(f))
        assert result is None

    def test_check_file_missing(self):
        """check_file returns error string for non-existent file."""
        result = check_file("/nonexistent/file/xyz.ase")
        assert result is not None
        assert "not found" in result

    def test_check_file_missing_contains_filename(self):
        """Error message includes the filename."""
        result = check_file("/path/to/missing.aseprite")
        assert "missing.aseprite" in result


class TestValidateHexColor:
    def test_validate_hex_color_valid_6digit(self):
        """Valid #RRGGBB returns correct (r, g, b) tuple."""
        assert validate_hex_color("#ff0000") == (255, 0, 0)
        assert validate_hex_color("#00ff00") == (0, 255, 0)
        assert validate_hex_color("#0000ff") == (0, 0, 255)
        assert validate_hex_color("#ffffff") == (255, 255, 255)
        assert validate_hex_color("#000000") == (0, 0, 0)

    def test_validate_hex_color_valid_without_hash(self):
        """Valid RRGGBB without hash prefix works."""
        assert validate_hex_color("ff0000") == (255, 0, 0)

    def test_validate_hex_color_invalid_too_short(self):
        """Too-short hex string returns None."""
        assert validate_hex_color("#fff") is None

    def test_validate_hex_color_invalid_too_long(self):
        """Too-long hex string returns None."""
        assert validate_hex_color("#ff0000ff") is None

    def test_validate_hex_color_invalid_characters(self):
        """Non-hex characters return None."""
        assert validate_hex_color("#gggggg") is None

    def test_validate_hex_color_empty_string(self):
        """Empty string returns None."""
        assert validate_hex_color("") is None

    def test_validate_hex_color_mixed_case(self):
        """Mixed case hex works."""
        assert validate_hex_color("#FfFfFf") == (255, 255, 255)

    def test_validate_hex_color_only_hash(self):
        """Just a hash returns None."""
        assert validate_hex_color("#") is None