"""Aseprite CLI wrapper for batch mode operations."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from aseprite_mcp.config import AsepriteConfig


class AsepriteCLIError(Exception):
    def __init__(self, message: str, returncode: int, stderr: str):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


class AsepriteCLI:
    def __init__(self, config: AsepriteConfig) -> None:
        self.config = config

    def run_batch(
        self,
        args: list[str],
        script_content: str | None = None,
        script_params: dict[str, str] | None = None,
        timeout: int = 60,
    ) -> subprocess.CompletedProcess[bytes]:
        cmd = [self.config.aseprite_path, "-b"]
        cmd.extend(args)

        script_path: str | None = None
        if script_content:
            self.config.ensure_tmp_dir()
            fd, script_path = tempfile.mkstemp(
                suffix=".lua", dir=str(self.config.tmp_dir)
            )
            with open(script_path, "w") as f:
                f.write(script_content)
            os.close(fd)
            cmd.extend(["--script", script_path])

        if script_params:
            for key, value in script_params.items():
                cmd.extend(["--script-param", f"{key}={value}"])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise AsepriteCLIError(
                f"Aseprite timed out after {timeout}s",
                returncode=-1,
                stderr="",
            ) from exc
        finally:
            if script_path:
                Path(script_path).unlink(missing_ok=True)

        return result

    def run_script(
        self,
        script_content: str,
        script_params: dict[str, str] | None = None,
        timeout: int = 60,
    ) -> str:
        result = self.run_batch(
            args=[],
            script_content=script_content,
            script_params=script_params,
            timeout=timeout,
        )
        if result.returncode != 0:
            raise AsepriteCLIError(
                f"Aseprite exited with code {result.returncode}: "
                f"{result.stderr.decode(errors='replace')}",
                returncode=result.returncode,
                stderr=result.stderr.decode(errors="replace"),
            )
        return result.stdout.decode(errors="replace")

    def run_json_script(
        self,
        script_content: str,
        script_params: dict[str, str] | None = None,
        timeout: int = 60,
    ) -> Any:
        raw = self.run_script(script_content, script_params, timeout)
        lines = raw.strip().splitlines()
        for line in reversed(lines):
            line = line.strip()
            if line.startswith("JSON_START") or line.startswith("{"):
                try:
                    json_str = line
                    if line.startswith("JSON_START"):
                        json_str = line[len("JSON_START"):]
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        raise ValueError(f"No JSON output found in Aseprite response: {raw[:500]}")

    def execute_lua_script(
        self,
        script_content: str,
        filename: str | None = None,
        timeout: int = 60,
    ) -> tuple[bool, str]:
        """Execute a Lua script in Aseprite batch mode.

        Args:
            script_content: Lua script code to execute
            filename: Optional sprite file to open before executing
            timeout: Timeout in seconds

        Returns:
            Tuple of (success: bool, output: str)
        """
        args: list[str] = []
        if filename:
            args.append(filename)

        result = self.run_batch(
            args=args,
            script_content=script_content,
            timeout=timeout,
        )

        success = result.returncode == 0
        output = (
            result.stdout.decode(errors="replace")
            if success
            else result.stderr.decode(errors="replace")
        )
        return success, output

    def list_layers(self, file_path: str) -> list[str]:
        result = self.run_batch(["--list-layers", file_path])
        if result.returncode != 0:
            raise AsepriteCLIError(
                f"Failed to list layers: {result.stderr.decode(errors='replace')}",
                returncode=result.returncode,
                stderr=result.stderr.decode(errors="replace"),
            )
        output = result.stdout.decode(errors="replace").strip()
        if not output:
            return []
        return output.splitlines()

    def list_tags(self, file_path: str) -> list[str]:
        result = self.run_batch(["--list-tags", file_path])
        if result.returncode != 0:
            raise AsepriteCLIError(
                f"Failed to list tags: {result.stderr.decode(errors='replace')}",
                returncode=result.returncode,
                stderr=result.stderr.decode(errors="replace"),
            )
        output = result.stdout.decode(errors="replace").strip()
        if not output:
            return []
        return output.splitlines()

    def list_slices(self, file_path: str) -> list[str]:
        result = self.run_batch(["--list-slices", file_path])
        if result.returncode != 0:
            raise AsepriteCLIError(
                f"Failed to list slices: {result.stderr.decode(errors='replace')}",
                returncode=result.returncode,
                stderr=result.stderr.decode(errors="replace"),
            )
        output = result.stdout.decode(errors="replace").strip()
        if not output:
            return []
        return output.splitlines()
