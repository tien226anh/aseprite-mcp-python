"""Tests for aseprite_mcp.config module."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from aseprite_mcp.config import AsepriteConfig


class TestAsepriteConfig:
    def test_default_values(self) -> None:
        config = AsepriteConfig(aseprite_path="/usr/bin/aseprite")
        assert config.aseprite_path == "/usr/bin/aseprite"
        assert config.ws_host == "127.0.0.1"
        assert config.ws_port == 8765
        assert config.tmp_dir == Path("/tmp/aseprite_mcp_scripts")
        assert config.output_dir == Path("generated_assets")

    def test_custom_values(self) -> None:
        config = AsepriteConfig(
            aseprite_path="/custom/aseprite",
            ws_host="0.0.0.0",
            ws_port=9999,
            tmp_dir=Path("/custom/tmp"),
            output_dir=Path("/custom/output"),
        )
        assert config.aseprite_path == "/custom/aseprite"
        assert config.ws_host == "0.0.0.0"
        assert config.ws_port == 9999
        assert config.tmp_dir == Path("/custom/tmp")
        assert config.output_dir == Path("/custom/output")

    def test_from_env_with_path(self, tmp_path: Path) -> None:
        fake_binary = tmp_path / "aseprite"
        fake_binary.write_text("#!/bin/bash")
        fake_binary.chmod(0o755)

        with patch.dict(os.environ, {"ASEPRITE_PATH": str(fake_binary)}, clear=False):
            config = AsepriteConfig.from_env()
            assert config.aseprite_path == str(fake_binary)

    def test_from_env_missing_raises(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("aseprite_mcp.config.shutil.which", return_value=None),
            patch.object(Path, "is_file", return_value=False),
            pytest.raises(FileNotFoundError, match="Aseprite binary"),
        ):
            AsepriteConfig.from_env()

    def test_from_env_custom_ws_settings(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ASEPRITE_PATH": "/usr/bin/aseprite",
                "ASEPRITE_WS_HOST": "0.0.0.0",
                "ASEPRITE_WS_PORT": "9999",
            },
            clear=False,
        ):
            config = AsepriteConfig.from_env()
            assert config.ws_host == "0.0.0.0"
            assert config.ws_port == 9999

    def test_from_env_custom_output_dir(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ASEPRITE_PATH": "/usr/bin/aseprite",
                "ASEPRITE_OUTPUT_DIR": "/custom/assets",
            },
            clear=False,
        ):
            config = AsepriteConfig.from_env()
            assert config.output_dir == Path("/custom/assets")

    def test_ensure_tmp_dir(self, tmp_path: Path) -> None:
        new_tmp = tmp_path / "aseprite_test_tmp"
        config = AsepriteConfig(
            aseprite_path="/usr/bin/aseprite", tmp_dir=new_tmp
        )
        config.ensure_tmp_dir()
        assert new_tmp.is_dir()

    def test_ensure_tmp_dir_idempotent(self, tmp_path: Path) -> None:
        new_tmp = tmp_path / "aseprite_test_tmp2"
        config = AsepriteConfig(
            aseprite_path="/usr/bin/aseprite", tmp_dir=new_tmp
        )
        config.ensure_tmp_dir()
        config.ensure_tmp_dir()
        assert new_tmp.is_dir()

    def test_ensure_output_dir(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "output"
        config = AsepriteConfig(
            aseprite_path="/usr/bin/aseprite", output_dir=out_dir
        )
        config.ensure_output_dir()
        assert out_dir.is_dir()

    def test_ensure_output_dir_idempotent(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "output2"
        config = AsepriteConfig(
            aseprite_path="/usr/bin/aseprite", output_dir=out_dir
        )
        config.ensure_output_dir()
        config.ensure_output_dir()
        assert out_dir.is_dir()

    def test_resolve_output_path(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "assets"
        config = AsepriteConfig(
            aseprite_path="/usr/bin/aseprite", output_dir=out_dir
        )
        result = config.resolve_output_path("sprite.ase")
        assert result == out_dir / "sprite.ase"
        assert out_dir.is_dir()

    def test_find_aseprite_binary_with_which(self) -> None:
        with patch(
            "aseprite_mcp.config.shutil.which",
            return_value="/usr/bin/aseprite",
        ):
            result = AsepriteConfig._find_aseprite_binary()
            assert result == "/usr/bin/aseprite"

    def test_find_aseprite_binary_fallback_path(self) -> None:
        with (
            patch("aseprite_mcp.config.shutil.which", return_value=None),
            patch.object(Path, "is_file", return_value=True),
        ):
                result = AsepriteConfig._find_aseprite_binary()
                assert result != ""
