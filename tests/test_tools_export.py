"""Tests for aseprite_mcp.tools.export module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aseprite_mcp.aseprite_cli import AsepriteCLI


@pytest.fixture
def mock_cli():
    """Create a mock AsepriteCLI with execute_lua_script returning success."""
    cli = MagicMock(spec=AsepriteCLI)
    cli.execute_lua_script.return_value = (True, "Success")
    return cli


@pytest.fixture(autouse=True)
def patch_get_cli(mock_cli):
    """Patch get_cli to return our mock for all tests in this module."""
    with patch("aseprite_mcp.tools.export.get_cli", return_value=mock_cli):
        yield mock_cli


class TestExportSprite:
    @pytest.mark.asyncio
    async def test_export_sprite_file_not_found(self):
        from aseprite_mcp.tools.export import export_sprite

        with patch("aseprite_mcp.tools.export.check_file", return_value="File missing"):
            result = await export_sprite(
                filename="missing.ase", output_filename="out.png"
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_export_sprite_unsupported_format(self):
        from aseprite_mcp.tools.export import export_sprite

        with patch("aseprite_mcp.tools.export.check_file", return_value=None):
            result = await export_sprite(
                filename="test.ase", output_filename="out.tiff", format="tiff"
            )
        assert "Error" in result
        assert "unsupported" in result.lower() or "format" in result.lower()

    @pytest.mark.asyncio
    async def test_export_sprite_success(self, mock_cli):
        import subprocess

        from aseprite_mcp.config import AsepriteConfig
        from aseprite_mcp.tools.export import export_sprite

        AsepriteConfig(aseprite_path="/usr/bin/aseprite")
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )
        mock_cli.run_batch = MagicMock(return_value=mock_result)

        with patch("aseprite_mcp.tools.export.check_file", return_value=None):
            result = await export_sprite(
                filename="test.ase", output_filename="out.png", format="png"
            )
        assert "Exported" in result


class TestCopySprite:
    @pytest.mark.asyncio
    async def test_copy_sprite_file_not_found(self):
        from aseprite_mcp.tools.export import copy_sprite

        with patch("aseprite_mcp.tools.export.check_file", return_value="File missing"):
            result = await copy_sprite(
                filename="missing.ase", output_filename="copy.aseprite"
            )
        assert "missing" in result

    @pytest.mark.asyncio
    async def test_copy_sprite_exists_no_overwrite(self, tmp_path):
        from aseprite_mcp.tools.export import copy_sprite

        # Create a file so os.path.exists returns True
        existing = tmp_path / "copy.aseprite"
        existing.write_text("dummy")

        with patch("aseprite_mcp.tools.export.check_file", return_value=None):
            result = await copy_sprite(
                filename="test.ase", output_filename=str(existing), overwrite=False
            )
        assert "already exists" in result

    @pytest.mark.asyncio
    async def test_copy_sprite_invalid_extension(self):
        from aseprite_mcp.tools.export import copy_sprite

        with patch("aseprite_mcp.tools.export.check_file", return_value=None):
            result = await copy_sprite(filename="test.ase", output_filename="copy.png")
        assert "Error" in result
        assert ".aseprite" in result or ".ase" in result

    @pytest.mark.asyncio
    async def test_copy_sprite_success(self, mock_cli):
        from aseprite_mcp.tools.export import copy_sprite

        with (
            patch("aseprite_mcp.tools.export.check_file", return_value=None),
            patch("os.path.exists", return_value=False),
        ):
            result = await copy_sprite(
                filename="test.ase", output_filename="copy.aseprite"
            )
        assert "Copied" in result
        mock_cli.execute_lua_script.assert_called_once()
