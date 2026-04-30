"""Entry point for aseprite-mcp."""

from __future__ import annotations

import argparse
import logging
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aseprite-mcp",
        description="MCP server for Aseprite pixel art editor",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="MCP transport mode (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for streamable-http transport (default: 8080)",
    )
    parser.add_argument(
        "--aseprite-path",
        type=str,
        default=None,
        help="Path to Aseprite binary (overrides ASEPRITE_PATH env var)",
    )
    parser.add_argument(
        "--ws-port",
        type=int,
        default=8765,
        help="WebSocket port for Aseprite bridge (default: 8765)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory for generated assets (default: generated_assets/)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        stream=sys.stderr,
        format="%(name)s - %(levelname)s - %(message)s",
    )

    if args.aseprite_path:
        import os

        os.environ["ASEPRITE_PATH"] = args.aseprite_path

    if args.ws_port:
        import os

        os.environ["ASEPRITE_WS_PORT"] = str(args.ws_port)

    if args.output_dir:
        import os

        os.environ["ASEPRITE_OUTPUT_DIR"] = args.output_dir

    from aseprite_mcp.server import run_server

    run_server(transport=args.transport, port=args.port)


if __name__ == "__main__":
    main()
