"""Configuration for Aseprite MCP server."""

from __future__ import annotations

import contextlib
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AsepriteConfig:
    aseprite_path: str
    ws_host: str = "127.0.0.1"
    ws_port: int = 8765
    tmp_dir: Path = field(default_factory=lambda: Path("/tmp/aseprite_mcp_scripts"))
    output_dir: Path = field(default_factory=lambda: Path("generated_assets"))

    @classmethod
    def from_env(cls) -> AsepriteConfig:
        aseprite_path = os.environ.get(
            "ASEPRITE_PATH", cls._find_aseprite_binary()
        )
        if not aseprite_path:
            raise FileNotFoundError(
                "Aseprite binary not found. Set ASEPRITE_PATH environment variable."
            )
        ws_host = os.environ.get("ASEPRITE_WS_HOST", "127.0.0.1")
        ws_port = int(os.environ.get("ASEPRITE_WS_PORT", "8765"))
        output_dir = Path(os.environ.get("ASEPRITE_OUTPUT_DIR", "generated_assets"))
        return cls(
            aseprite_path=aseprite_path,
            ws_host=ws_host,
            ws_port=ws_port,
            output_dir=output_dir,
        )

    @staticmethod
    def _find_aseprite_binary() -> str:
        binary = shutil.which("aseprite")
        if binary:
            return binary
        common_paths = [
            "/usr/lib/aseprite/aseprite",
            "/usr/local/bin/aseprite",
            "/snap/bin/aseprite",
        ]
        with contextlib.suppress(RuntimeError):
            common_paths.append(
                str(Path.home() / "aseprite" / "build" / "bin" / "aseprite")
            )
        for p in common_paths:
            try:
                if Path(p).is_file():
                    return p
            except OSError:
                continue
        return ""

    def ensure_tmp_dir(self) -> None:
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def ensure_output_dir(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def resolve_output_path(self, filename: str) -> Path:
        """Return a path inside output_dir, ensuring the directory exists."""
        self.ensure_output_dir()
        return self.output_dir / filename
