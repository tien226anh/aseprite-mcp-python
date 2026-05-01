"""Tests for aseprite_mcp.aseprite_cli module."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aseprite_mcp.aseprite_cli import AsepriteCLI, AsepriteCLIError
from aseprite_mcp.config import AsepriteConfig


@pytest.fixture
def config(tmp_path: Path) -> AsepriteConfig:
    return AsepriteConfig(
        aseprite_path="/usr/bin/aseprite",
        tmp_dir=tmp_path / "scripts",
    )


@pytest.fixture
def cli(config: AsepriteConfig) -> AsepriteCLI:
    return AsepriteCLI(config)


class TestAsepriteCLI:
    def test_run_batch_builds_command(
        self, cli: AsepriteCLI, config: AsepriteConfig
    ) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"output", stderr=b""
        )
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = cli.run_batch(["--list-layers", "test.ase"])
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert cmd[0] == config.aseprite_path
            assert "-b" in cmd
            assert "--list-layers" in cmd
            assert "test.ase" in cmd
            assert result.returncode == 0

    def test_run_batch_with_script(self, cli: AsepriteCLI) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"ok", stderr=b""
        )
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            cli.run_batch(args=[], script_content='print("hello")')
            mock_run.assert_called_once()
            cmd = mock_run.call_args[0][0]
            assert "--script" in cmd

    def test_run_batch_with_params(self, cli: AsepriteCLI) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            cli.run_batch(
                args=[],
                script_content='print("x")',
                script_params={"output": "/tmp/out.ase", "mode": "rgb"},
            )
            cmd = mock_run.call_args[0][0]
            assert "--script-param" in cmd
            idx = cmd.index("--script-param")
            assert "output=/tmp/out.ase" in cmd[idx + 1]
            assert "mode=rgb" in cmd[idx + 3]

    def test_run_script_success(self, cli: AsepriteCLI) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"Hello Aseprite", stderr=b""
        )
        with patch.object(cli, "run_batch", return_value=mock_result):
            output = cli.run_script('print("hello")')
            assert "Hello Aseprite" in output

    def test_run_script_error(self, cli: AsepriteCLI) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=1, stdout=b"", stderr=b"Error occurred"
        )
        with patch.object(cli, "run_batch", return_value=mock_result):
            with pytest.raises(AsepriteCLIError) as exc_info:
                cli.run_script("invalid()")
            assert exc_info.value.returncode == 1
            assert "Error occurred" in exc_info.value.stderr

    def test_run_json_script_parses_output(self, cli: AsepriteCLI) -> None:
        json_output = '{"width": 32, "height": 32}'
        with patch.object(
            cli,
            "run_script",
            return_value=f"some log\nJSON_START{json_output}\n",
        ):
            result = cli.run_json_script("script")
            assert result == {"width": 32, "height": 32}

    def test_run_json_script_no_json_raises(self, cli: AsepriteCLI) -> None:
        with (
            patch.object(cli, "run_script", return_value="no json here"),
            pytest.raises(ValueError, match="No JSON output"),
        ):
            cli.run_json_script("script")

    def test_run_json_script_bare_json(self, cli: AsepriteCLI) -> None:
        json_output = '{"result": true}'
        with patch.object(cli, "run_script", return_value=json_output):
            result = cli.run_json_script("script")
            assert result == {"result": True}

    def test_run_batch_timeout(self, cli: AsepriteCLI) -> None:
        with (
            patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 60)),
            pytest.raises(AsepriteCLIError, match="timed out"),
        ):
            cli.run_batch(args=[], timeout=60)

    def test_script_file_cleanup(
        self, cli: AsepriteCLI, config: AsepriteConfig
    ) -> None:
        config.ensure_tmp_dir()
        created_files: list[str] = []

        def track_and_return(
            *args: object, **kwargs: object
        ) -> subprocess.CompletedProcess[bytes]:
            for call_args in mock_run.call_args_list:
                cmd = call_args[0][0]
                if "--script" in cmd:
                    idx = cmd.index("--script")
                    created_files.append(cmd[idx + 1])
            return subprocess.CompletedProcess(
                args=[], returncode=0, stdout=b"ok", stderr=b""
            )

        mock_run = MagicMock(side_effect=track_and_return)

    def test_list_layers(self, cli: AsepriteCLI) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"Background\nLayer 1\nLayer 2",
            stderr=b"",
        )
        with patch.object(cli, "run_batch", return_value=mock_result):
            layers = cli.list_layers("test.ase")
            assert layers == ["Background", "Layer 1", "Layer 2"]

    def test_list_tags(self, cli: AsepriteCLI) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"walk\ncycle\nidle",
            stderr=b"",
        )
        with patch.object(cli, "run_batch", return_value=mock_result):
            tags = cli.list_tags("test.ase")
            assert tags == ["walk", "cycle", "idle"]

    def test_list_slices(self, cli: AsepriteCLI) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"hitbox\nattack_box",
            stderr=b"",
        )
        with patch.object(cli, "run_batch", return_value=mock_result):
            slices = cli.list_slices("test.ase")
            assert slices == ["hitbox", "attack_box"]

    def test_list_layers_empty(self, cli: AsepriteCLI) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )
        with patch.object(cli, "run_batch", return_value=mock_result):
            layers = cli.list_layers("test.ase")
            assert layers == []

    def test_cli_error_has_fields(self) -> None:
        err = AsepriteCLIError("test error", returncode=42, stderr="stderr output")
        assert str(err) == "test error"
        assert err.returncode == 42
        assert err.stderr == "stderr output"


class TestExecuteLuaScript:
    """Tests for AsepriteCLI.execute_lua_script method."""

    def test_execute_lua_script_success(self, cli: AsepriteCLI) -> None:
        """execute_lua_script returns (True, stdout) on success."""
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"Script output here", stderr=b""
        )
        with patch.object(cli, "run_batch", return_value=mock_result):
            success, output = cli.execute_lua_script('print("hello")')
        assert success is True
        assert "Script output here" in output

    def test_execute_lua_script_with_filename(self, cli: AsepriteCLI) -> None:
        """execute_lua_script passes filename as arg to run_batch."""
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"ok", stderr=b""
        )
        with patch.object(cli, "run_batch", return_value=mock_result) as mock_batch:
            success, _output = cli.execute_lua_script(
                'print("hello")', filename="test.ase"
            )
        assert success is True
        call_args = mock_batch.call_args
        assert "test.ase" in call_args[1].get(
            "args", call_args[0][0] if call_args[0] else call_args[1].get("args", [])
        )
        # Verify script_content was passed
        assert (
            call_args[1].get(
                "script_content",
                (
                    call_args[0][1]
                    if len(call_args[0]) > 1
                    else call_args[1].get("script_content")
                ),
            )
            is not None
        )

    def test_execute_lua_script_failure(self, cli: AsepriteCLI) -> None:
        """execute_lua_script returns (False, stderr) on failure."""
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=1, stdout=b"", stderr=b"Aseprite error occurred"
        )
        with patch.object(cli, "run_batch", return_value=mock_result):
            success, output = cli.execute_lua_script("invalid()")
        assert success is False
        assert "Aseprite error" in output

    def test_execute_lua_script_no_filename(self, cli: AsepriteCLI) -> None:
        """execute_lua_script works without a filename (empty args)."""
        mock_result = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"ok", stderr=b""
        )
        with patch.object(cli, "run_batch", return_value=mock_result) as mock_batch:
            success, _output = cli.execute_lua_script('print("hello")')
        assert success is True
        # Verify empty args list was passed
        call_kwargs = mock_batch.call_args[1]
        assert (
            call_kwargs.get(
                "args", mock_batch.call_args[0][0] if mock_batch.call_args[0] else []
            )
            == []
        )
