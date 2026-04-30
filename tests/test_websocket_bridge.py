"""Tests for aseprite_mcp.websocket_bridge module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aseprite_mcp.config import AsepriteConfig
from aseprite_mcp.websocket_bridge import WebSocketBridge


@pytest.fixture
def config() -> AsepriteConfig:
    return AsepriteConfig(
        aseprite_path="/usr/bin/aseprite",
        ws_host="127.0.0.1",
        ws_port=18765,
    )


@pytest.fixture
def bridge(config: AsepriteConfig) -> WebSocketBridge:
    return WebSocketBridge(config)


class TestWebSocketBridge:
    def test_ws_url(self, bridge: WebSocketBridge) -> None:
        assert bridge.ws_url == "ws://127.0.0.1:18765"

    def test_initial_state(self, bridge: WebSocketBridge) -> None:
        assert bridge._server is None
        assert bridge._aseprite_connection is None
        assert bridge._aseprite_process is None
        assert bridge._running is False

    @pytest.mark.asyncio
    async def test_start(self, bridge: WebSocketBridge) -> None:
        with patch("websockets.serve", new_callable=AsyncMock) as mock_serve:
            mock_server = MagicMock()
            mock_serve.return_value = mock_server
            await bridge.start()
            assert bridge._running is True
            mock_serve.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop(self, bridge: WebSocketBridge) -> None:
        bridge._running = True
        mock_server = AsyncMock()
        mock_server.close = MagicMock()
        mock_server.wait_closed = AsyncMock()
        bridge._server = mock_server
        await bridge.stop()
        assert bridge._running is False
        mock_server.close.assert_called_once()
        mock_server.wait_closed.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_command_no_connection_raises(
        self, bridge: WebSocketBridge
    ) -> None:
        with pytest.raises(ConnectionError, match="No Aseprite WebSocket"):
            await bridge.send_command({"action": "ping"})

    @pytest.mark.asyncio
    async def test_send_command_success(self, bridge: WebSocketBridge) -> None:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        mock_ws.recv = AsyncMock(return_value='{"status": "ok"}')
        bridge._aseprite_connection = mock_ws

        result = await bridge.send_command({"action": "ping"})
        assert result == {"status": "ok"}
        mock_ws.send.assert_called_once_with('{"action": "ping"}')

    def test_launch_aseprite_with_bridge(self, bridge: WebSocketBridge) -> None:
        bridge.config.ensure_tmp_dir()
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_popen.return_value = mock_process

            proc = bridge.launch_aseprite_with_bridge("/path/to/sprite.ase")
            assert proc is mock_process
            mock_popen.assert_called_once()
            cmd = mock_popen.call_args[0][0]
            assert "/usr/bin/aseprite" in cmd
            assert "--script" in cmd
            assert "/path/to/sprite.ase" in cmd

    @pytest.mark.asyncio
    async def test_handler_sets_connection(self, bridge: WebSocketBridge) -> None:
        class FakeWS:
            async def __aiter__(self):
                if False:
                    yield

        mock_ws = FakeWS()

        await bridge._handler(mock_ws)
        assert bridge._aseprite_connection is None
