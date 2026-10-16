"""Locate a HOST-runnable `claude` CLI. If none is found the engine runs in
simulation mode (replayed streams) so the pipeline still works end-to-end.

Note: the Claude *desktop app* ships a Linux/ARM `claude` under
'Application Support/Claude/claude-code-vm/*/claude' — that is NOT host-runnable
on macOS, so it is deliberately skipped."""
from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from config import CLAUDE_BIN

_CANDIDATES = [
    CLAUDE_BIN,
    str(Path.home() / ".claude" / "local" / "claude"),
    str(Path.home() / ".local" / "bin" / "claude"),
    "/opt/homebrew/bin/claude",
    "/usr/local/bin/claude",
    str(Path.home() / ".npm-global" / "bin" / "claude"),
]


def _runnable(path: str) -> bool:
    try:
        r = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=15)
        return r.returncode == 0 and "exec format" not in (r.stderr or "")
    except Exception:
        return False


def find_claude() -> str | None:
    env = os.environ.get("CC_CLAUDE_BIN")
    if env and _runnable(env):
        return env
    which = shutil.which("claude")
    if which and _runnable(which):
        return which
    for c in _CANDIDATES:
        if c and Path(c).exists() and _runnable(c):
            return c
    return None


def engine_status() -> dict:
    forced = os.environ.get("CC_ENGINE")  # 'sim' | 'real' | None(auto)
    claude = None if forced == "sim" else find_claude()
    version = None
    if claude:
        try:
            version = subprocess.run([claude, "--version"], capture_output=True, text=True, timeout=15).stdout.strip()
        except Exception:
            pass
    mode = "sim" if (forced == "sim" or not claude) else "real"
    return {
        "mode": mode,
        "claude_bin": claude,
        "claude_version": version,
        "note": ("Live engine: spawning the local claude CLI on your subscription login."
                 if mode == "real" else
                 "Simulation engine: no host-runnable `claude` CLI found. "
                 "Install it (npm i -g @anthropic-ai/claude-code; claude login) or set CC_CLAUDE_BIN "
                 "to go live. Jobs replay a realistic stream so the full pipeline is demonstrable."),
    }
