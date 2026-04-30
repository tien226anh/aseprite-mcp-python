"""WebSocket bridge for real-time Aseprite communication."""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
from typing import Any

import websockets

from aseprite_mcp.config import AsepriteConfig

logger = logging.getLogger(__name__)


class WebSocketBridge:
    def __init__(self, config: AsepriteConfig) -> None:
        self.config = config
        self._server: websockets.Server | None = None
        self._aseprite_connection: Any = None
        self._aseprite_process: subprocess.Popen | None = None
        self._running = False

    @property
    def ws_url(self) -> str:
        return f"ws://{self.config.ws_host}:{self.config.ws_port}"

    async def start(self) -> None:
        self._running = True
        self._server = await websockets.serve(
            self._handler,
            self.config.ws_host,
            self.config.ws_port,
        )
        logger.info("WebSocket server started on %s", self.ws_url)

    async def stop(self) -> None:
        self._running = False
        if self._aseprite_process:
            self._aseprite_process.terminate()
            self._aseprite_process = None
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        logger.info("WebSocket server stopped")

    async def send_command(self, command: dict[str, Any]) -> dict[str, Any]:
        if not self._aseprite_connection:
            raise ConnectionError("No Aseprite WebSocket connection active")
        await self._aseprite_connection.send(json.dumps(command))
        response_raw: str = await asyncio.wait_for(
            self._aseprite_connection.recv(), timeout=30
        )
        result: dict[str, Any] = json.loads(response_raw)
        return result

    def launch_aseprite_with_bridge(
        self, sprite_path: str | None = None
    ) -> subprocess.Popen:
        from aseprite_mcp.lua_scripts import ws_bridge_script

        script = ws_bridge_script(self.ws_url)

        config = self.config
        config.ensure_tmp_dir()

        import tempfile

        fd, script_path = tempfile.mkstemp(
            suffix=".lua", dir=str(config.tmp_dir)
        )
        with open(script_path, "w") as f:
            f.write(script)
        import os

        os.close(fd)

        cmd = [config.aseprite_path]
        if sprite_path:
            cmd.append(sprite_path)
        cmd.extend(["--script", script_path])

        self._aseprite_process = subprocess.Popen(cmd)
        logger.info("Launched Aseprite with PID %d", self._aseprite_process.pid)
        return self._aseprite_process

    async def _handler(
        self, websocket: websockets.ServerConnection
    ) -> None:
        self._aseprite_connection = websocket
        logger.info("Aseprite connected via WebSocket")
        try:
            async for message in websocket:
                logger.debug("Received from Aseprite: %s", message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Aseprite WebSocket connection closed")
        finally:
            self._aseprite_connection = None
