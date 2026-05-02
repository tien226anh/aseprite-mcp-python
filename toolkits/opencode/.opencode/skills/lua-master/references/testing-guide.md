# Testing Lua Tool Functions

## Test Structure

Tests mock `subprocess.run` / `subprocess.Popen` — no Aseprite binary needed. Tests live in `tests/` with `pytest-asyncio` (async mode: `auto`).

## Standard Fixture Pattern

```python
import pytest
from unittest.mock import MagicMock, patch
from aseprite_mcp.aseprite_cli import AsepriteCLI

@pytest.fixture
def mock_cli():
    cli = MagicMock(spec=AsepriteCLI)
    cli.execute_lua_script.return_value = (True, "Success")
    return cli

@pytest.fixture(autouse=True)
def patch_get_cli(mock_cli):
    with patch("aseprite_mcp.tools.<module>.get_cli", return_value=mock_cli):
        yield mock_cli
```

## Test Organization

```python
@pytest.mark.asyncio
class TestMyTool:
    async def test_validation_error_invalid_filename(self, mock_cli):
        result = await my_tool(filename="nonexistent.ase")
        assert "not found" in result.lower() or "error" in result.lower()
        mock_cli.execute_lua_script.assert_not_called()

    async def test_validation_error_path_traversal(self, mock_cli):
        result = await my_tool(filename="../etc/passwd.ase")
        assert "path traversal" in result.lower()

    async def test_success(self, mock_cli):
        with patch("aseprite_mcp.tools.<module>.check_file", return_value=None):
            result = await my_tool(filename="test.ase", ...)
            assert result.startswith("Success") or "success" in result.lower()

    async def test_failure(self, mock_cli):
        mock_cli.execute_lua_script.return_value = (False, "Error message")
        with patch("aseprite_mcp.tools.<module>.check_file", return_value=None):
            result = await my_tool(filename="test.ase", ...)
            assert "Failed" in result
```

## Asserting Lua Script Content

```python
async def test_lua_script_content(self, mock_cli):
    with patch("aseprite_mcp.tools.<module>.check_file", return_value=None):
        await my_tool(filename="test.ase", layer_name="outline", frame_index=1)

    script = mock_cli.execute_lua_script.call_args[0][0]
    assert "app.activeSprite" in script
    assert "app.transaction" in script
    assert 'spr:saveAs' in script
```

## Key Testing Conventions

- Use `@pytest.mark.asyncio` on all async test methods
- Organize tests into `TestXxx` classes by tool function
- Test validation errors first (invalid inputs), then success cases, then failure cases
- For `check_file` patching: `with patch("aseprite_mcp.tools.<module>.check_file", return_value=None):`
- Assert on both the result string AND the Lua script content
- E2E tests import ALL tool modules at the top so `patch()` can resolve dotted paths at runtime

## Test File Naming

| Module | Test File |
|--------|-----------|
| `canvas.py` | `test_tools_canvas.py` |
| `drawing.py` | `test_tools_drawing.py` |
| `animation.py` | `test_tools_animation.py` |
| `export.py` | `test_tools_export.py` |
| `palette.py` | `test_tools_palette.py` |
| `pixel_read.py` | `test_tools_pixel_read.py` |
| `preview.py` | `test_tools_preview.py` |
| `transform.py` | `test_tools_transform.py` |
| `quality.py` | `test_tools_quality.py` |
| `scene.py` | `test_tools_scene.py` |
| `guide.py` | (no tests needed — pure text) |

## Running Tests

```bash
# All tests
uv run pytest tests/ -v

# Specific module
uv run pytest tests/test_tools_canvas.py -v

# Specific test class
uv run pytest tests/test_tools_canvas.py::TestCreateCanvas -v

# With coverage
uv run pytest tests/ -v --cov=aseprite_mcp
```