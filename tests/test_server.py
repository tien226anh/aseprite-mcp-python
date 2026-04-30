"""Tests for aseprite_mcp.server module (MCP tools/resources/prompts)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from aseprite_mcp.aseprite_cli import AsepriteCLI
from aseprite_mcp.config import AsepriteConfig


@pytest.fixture
def config(tmp_path) -> AsepriteConfig:
    return AsepriteConfig(
        aseprite_path="/usr/bin/aseprite",
        tmp_dir=tmp_path / "scripts",
    )


@pytest.fixture
def cli(config: AsepriteConfig) -> AsepriteCLI:
    return AsepriteCLI(config)


class TestServerTools:
    @pytest.mark.asyncio
    async def test_sprite_create_validates_dimensions(self) -> None:
        from aseprite_mcp.server import sprite_create

        result = await sprite_create(width=0, height=32)
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_sprite_create_validates_color_mode(self) -> None:
        from aseprite_mcp.server import sprite_create

        result = await sprite_create(width=32, height=32, color_mode="cmyk")
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_sprite_create_success(self, config: AsepriteConfig) -> None:
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.run_json_script.return_value = {
            "width": 32,
            "height": 32,
            "colorMode": "rgb",
            "filename": "/tmp/test.ase",
        }
        srv._cli = mock_cli
        srv._config = config

        result = await srv.sprite_create(width=32, height=32)
        parsed = json.loads(result)
        assert parsed["width"] == 32
        assert parsed["height"] == 32

    @pytest.mark.asyncio
    async def test_sprite_export_validates_path(self) -> None:
        from aseprite_mcp.server import sprite_export

        result = await sprite_export(
            input_path="test.pdf", output_path="out.png"
        )
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_sprite_list_layers(self, config: AsepriteConfig) -> None:
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.list_layers.return_value = ["Background", "Layer 1"]
        srv._cli = mock_cli

        result = await srv.sprite_list_layers(file_path="test.ase")
        parsed = json.loads(result)
        assert "layers" in parsed
        assert len(parsed["layers"]) == 2

    @pytest.mark.asyncio
    async def test_sprite_list_tags(self, config: AsepriteConfig) -> None:
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.list_tags.return_value = ["walk", "idle"]
        srv._cli = mock_cli

        result = await srv.sprite_list_tags(file_path="test.ase")
        parsed = json.loads(result)
        assert "tags" in parsed
        assert "walk" in parsed["tags"]

    @pytest.mark.asyncio
    async def test_script_execute(self, config: AsepriteConfig) -> None:
        from aseprite_mcp import server as srv

        mock_cli = MagicMock(spec=AsepriteCLI)
        mock_cli.run_script.return_value = "Script output"
        srv._cli = mock_cli

        result = await srv.script_execute(lua_code='print("hello")')
        assert result == "Script output"

    @pytest.mark.asyncio
    async def test_ws_connect_returns_url(self) -> None:
        from aseprite_mcp import server as srv
        from aseprite_mcp.websocket_bridge import WebSocketBridge

        mock_bridge = AsyncMock(spec=WebSocketBridge)
        mock_bridge.start = AsyncMock()
        mock_bridge.ws_url = "ws://127.0.0.1:18766"
        mock_bridge.launch_aseprite_with_bridge = MagicMock()
        srv._ws_bridge = mock_bridge

        result = await srv.ws_connect()
        parsed = json.loads(result)
        assert parsed["ws_url"] == "ws://127.0.0.1:18766"
        assert parsed["status"] == "launched"

    @pytest.mark.asyncio
    async def test_draw_pixels_no_connection(self) -> None:
        from aseprite_mcp import server as srv
        from aseprite_mcp.websocket_bridge import WebSocketBridge

        mock_bridge = AsyncMock(spec=WebSocketBridge)
        mock_bridge.send_command = AsyncMock(
            side_effect=ConnectionError("No connection")
        )
        srv._ws_bridge = mock_bridge

        result = await srv.draw_pixels(pixels=[{"x": 0, "y": 0, "color": "#ff0000"}])
        assert "Error" in result
        assert "ws_connect" in result


class TestServerResources:
    def test_palette_resource_dawnbringer(self) -> None:
        from aseprite_mcp.server import get_palette_resource

        result = json.loads(get_palette_resource("dawnbringer32"))
        assert "colors" in result
        assert len(result["colors"]) == 16

    def test_palette_resource_pico8(self) -> None:
        from aseprite_mcp.server import get_palette_resource

        result = json.loads(get_palette_resource("pico8"))
        assert "colors" in result
        assert len(result["colors"]) == 16

    def test_palette_resource_not_found(self) -> None:
        from aseprite_mcp.server import get_palette_resource

        result = json.loads(get_palette_resource("nonexistent"))
        assert "error" in result


class TestServerPrompts:
    def test_pixel_art_asset_gen_prompt(self) -> None:
        from aseprite_mcp.server import pixel_art_asset_gen

        result = pixel_art_asset_gen(asset_type="tree", size="32x32")
        assert "tree" in result
        assert "32x32" in result
        assert "sprite_create" in result
