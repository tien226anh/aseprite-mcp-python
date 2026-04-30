"""Tests for aseprite_mcp.__main__ entry point."""

from __future__ import annotations

from unittest.mock import patch


class TestMain:
    def test_main_parses_args(self) -> None:
        with (
            patch("sys.argv", ["aseprite-mcp", "--transport", "stdio"]),
            patch("aseprite_mcp.server.run_server") as mock_run,
        ):
                from aseprite_mcp.__main__ import main

                main()
                mock_run.assert_called_once_with(transport="stdio", port=8080)

    def test_main_http_transport(self) -> None:
        with (
            patch(
                "sys.argv",
                ["aseprite-mcp", "--transport", "streamable-http", "--port", "9090"],
            ),
            patch("aseprite_mcp.server.run_server") as mock_run,
        ):
                from aseprite_mcp.__main__ import main

                main()
                mock_run.assert_called_once_with(
                    transport="streamable-http", port=9090
                )

    def test_main_sets_aseprite_path(self) -> None:
        with (
            patch(
                "sys.argv",
                ["aseprite-mcp", "--aseprite-path", "/custom/aseprite"],
            ),
            patch("aseprite_mcp.server.run_server"),
        ):
            import os

            from aseprite_mcp.__main__ import main

            main()
            assert os.environ.get("ASEPRITE_PATH") == "/custom/aseprite"

    def test_main_sets_output_dir(self) -> None:
        with (
            patch(
                "sys.argv",
                ["aseprite-mcp", "--output-dir", "/custom/assets"],
            ),
            patch("aseprite_mcp.server.run_server"),
        ):
            import os

            from aseprite_mcp.__main__ import main

            main()
            assert os.environ.get("ASEPRITE_OUTPUT_DIR") == "/custom/assets"
