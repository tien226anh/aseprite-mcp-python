"""Tests for aseprite_mcp.tools.preview module."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest


class TestStartPreviewServer:
    @pytest.mark.asyncio
    async def test_start_preview_server_nonexistent_directory(self):
        from aseprite_mcp.tools.preview import start_preview_server

        result = await start_preview_server(directory="/nonexistent/path/xyz")
        assert "Error" in result
        assert "does not exist" in result

    @pytest.mark.asyncio
    async def test_start_preview_server_success(self, tmp_path):
        from aseprite_mcp.tools.preview import start_preview_server, _pid_path

        # Clean up any existing PID file
        pid_file = _pid_path(8000)
        if os.path.exists(pid_file):
            os.remove(pid_file)

        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.wait.side_effect = subprocess.TimeoutExpired("cmd", 0.5)

        with patch("subprocess.Popen", return_value=mock_proc):
            result = await start_preview_server(directory=str(tmp_path), port=8000)
        assert "started" in result.lower() or "Preview" in result

        # Clean up PID file
        if os.path.exists(pid_file):
            os.remove(pid_file)

    @pytest.mark.asyncio
    async def test_start_preview_server_already_running(self, tmp_path):
        from aseprite_mcp.tools.preview import start_preview_server, _pid_path

        pid_file = _pid_path(8001)

        # Create a PID file with a running process PID (our own)
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

        try:
            with patch(
                "aseprite_mcp.tools.preview._pid_is_running", return_value=True
            ):
                result = await start_preview_server(
                    directory=str(tmp_path), port=8001
                )
            assert "already running" in result
        finally:
            if os.path.exists(pid_file):
                os.remove(pid_file)


class TestStopPreviewServer:
    @pytest.mark.asyncio
    async def test_stop_preview_server_no_pid_file(self):
        from aseprite_mcp.tools.preview import stop_preview_server, _pid_path

        pid_file = _pid_path(9999)
        # Ensure no PID file exists
        if os.path.exists(pid_file):
            os.remove(pid_file)

        result = await stop_preview_server(port=9999)
        assert "no" in result.lower() and "PID" in result.upper() or "No preview server" in result

    @pytest.mark.asyncio
    async def test_stop_preview_server_stale_pid(self):
        from aseprite_mcp.tools.preview import stop_preview_server, _pid_path

        pid_file = _pid_path(9998)
        # Write a stale PID (non-existent PID)
        with open(pid_file, "w") as f:
            f.write("99999999")

        try:
            result = await stop_preview_server(port=9998)
            assert "stale" in result.lower() or "No running" in result
        finally:
            if os.path.exists(pid_file):
                os.remove(pid_file)