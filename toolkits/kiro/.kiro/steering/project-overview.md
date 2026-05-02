---
inclusion: always
---

# Aseprite MCP Project Overview

Aseprite MCP server — bridges LLMs to Aseprite via the Model Context Protocol. 67 tools across 11 domain modules + 10 legacy tools.

## Architecture
```
src/aseprite_mcp/
├── __init__.py          # MCP singleton
├── __main__.py          # Entry point
├── server.py            # Legacy tools
├── aseprite_cli.py      # CLI wrapper
├── config.py            # Env vars
└── tools/
    ├── _helpers.py      # Shared utilities
    ├── animation.py     # Frame ops, tweening, tags
    ├── canvas.py         # Sprite creation, layers
    ├── drawing.py        # Pixel, shapes, gradients
    ├── export.py         # Export and copy
    ├── palette.py        # Color management
    ├── pixel_read.py     # Read pixels
    ├── preview.py        # HTTP preview
    ├── quality.py        # Validation, audit
    ├── scene.py          # Cross-sprite copying
    ├── guide.py          # Workflow guides
    └── transform.py      # Flip, rotate, resize
```

## Commands
```bash
uv sync                          # Install dependencies
uv run pytest tests/ -v           # Run tests
uv run ruff check src/ tests/     # Lint
uv run mypy src/                  # Typecheck
uv run aseprite-mcp               # Run server (stdio)
```

## Key Gotchas
- No Aseprite binary = hard failure: `ASEPRITE_PATH` must be set
- `execute_lua_script()` returns `(success: bool, output: str)`
- Frame indices are 1-based, pixel coordinates are 0-based
- Color format: hex `#RRGGBB` for new tools
- Two color validation systems — don't mix them
- Layer targeting: by name string, case-sensitive
- Path traversal: reject `..` in filenames
- Windows: always normalize backslashes
- Error handling: return strings, never raise
