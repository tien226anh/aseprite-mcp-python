"""Preview tools for Aseprite MCP — start/stop HTTP server for sprite previews."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile

from aseprite_mcp import mcp


def _pid_path(port: int) -> str:
    """Return the PID file path for a given port."""
    return os.path.join(tempfile.gettempdir(), f"aseprite_mcp_preview_{port}.pid")


def _pid_is_running(pid: int) -> bool:
    """Check whether a process with the given PID is still running."""
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                check=False,
                capture_output=True,
                text=True,
            )
            return str(pid) in result.stdout
        os.kill(pid, 0)
        return True
    except Exception:
        return False


@mcp.tool()
async def start_preview_server(directory: str, port: int = 8000) -> str:
    """Start a simple HTTP server to preview exported sprite files in a browser.

    Args:
        directory: Path to the directory containing exported sprites to serve.
        port: Port number for the HTTP server (default 8000).
    """
    if not os.path.isdir(directory):
        return f"Error: directory '{directory}' does not exist or is not a directory"

    pid_file = _pid_path(port)

    # Check if a server is already running on this port
    if os.path.exists(pid_file):
        try:
            with open(pid_file) as f:
                old_pid = int(f.read().strip())
            if _pid_is_running(old_pid):
                return (
                    f"Preview server already running on port {port} "
                    f"(PID {old_pid}) at http://localhost:{port}/"
                )
        except (ValueError, OSError):
            pass
        # Stale PID file — remove it
        try:
            os.remove(pid_file)
        except OSError:
            pass

    # Build the subprocess arguments
    cmd = [sys.executable, "-m", "http.server", str(port)]

    popen_kwargs: dict = {
        "cwd": directory,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }

    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS  # type: ignore[attr-defined]
    else:
        popen_kwargs["start_new_session"] = True  # type: ignore[assignment]

    proc = subprocess.Popen(cmd, **popen_kwargs)  # type: ignore[arg-type]

    # Write PID file
    with open(pid_file, "w") as f:
        f.write(str(proc.pid))

    # Brief pause to let the server start and detect early failures
    try:
        proc.wait(timeout=0.5)
        # If we get here, the process exited quickly — something went wrong
        try:
            os.remove(pid_file)
        except OSError:
            pass
        return f"Error: preview server process exited immediately (code {proc.returncode})"
    except subprocess.TimeoutExpired:
        # Process is still running — expected
        pass

    return f"Preview server started at http://localhost:{port}/ serving '{directory}'"


@mcp.tool()
async def stop_preview_server(port: int = 8000) -> str:
    """Stop a running preview HTTP server.

    Args:
        port: Port number of the server to stop (default 8000).
    """
    pid_file = _pid_path(port)

    if not os.path.exists(pid_file):
        return f"No preview server found on port {port} (no PID file)"

    try:
        with open(pid_file) as f:
            pid = int(f.read().strip())
    except (ValueError, OSError):
        # Corrupt PID file — clean it up
        try:
            os.remove(pid_file)
        except OSError:
            pass
        return f"Stale PID file for port {port} removed"

    if not _pid_is_running(pid):
        try:
            os.remove(pid_file)
        except OSError:
            pass
        return f"No running server found for port {port} (stale PID file removed)"

    # Kill the process
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                check=False,
                capture_output=True,
            )
        else:
            os.kill(pid, signal.SIGTERM)
    except Exception as exc:
        return f"Error stopping server PID {pid}: {exc}"

    # Clean up PID file
    try:
        os.remove(pid_file)
    except OSError:
        pass

    return f"Preview server on port {port} stopped (PID {pid})"