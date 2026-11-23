"""Proves the hook blocks force-pushes and lets normal commands through.

It runs the hook exactly as Claude Code does: JSON on stdin, read the exit code.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "block_force_push.py"


def run_hook(event):
    data = event if isinstance(event, str) else json.dumps(event)
    return subprocess.run([sys.executable, str(HOOK)], input=data,
                          capture_output=True, text=True)


def bash(command):
    return {"tool_name": "Bash", "tool_input": {"command": command}}


@pytest.mark.parametrize("command", [
    "git push --force",
    "git push -f origin main",
    "git push -uf origin feature",
    "git push origin +main",
    "git push --force-with-lease",
    "git commit -m 'fix' && git push -f",
    "cd .. ; git -C repo push --force",
])
def test_force_push_is_blocked(command):
    result = run_hook(bash(command))
    assert result.returncode == 2
    assert "Blocked by hook" in result.stderr


@pytest.mark.parametrize("command", [
    "git push",
    "git push origin feature",
    "git status",
    "echo 'never git push --force'",
    "pytest -q",
])
def test_normal_commands_pass(command):
    assert run_hook(bash(command)).returncode == 0


def test_other_tools_pass():
    assert run_hook({"tool_name": "Read", "tool_input": {"file_path": "x"}}).returncode == 0


def test_unreadable_input_is_blocked():
    assert run_hook("not json").returncode == 2
    assert run_hook(bash("git push 'unclosed")).returncode == 2
    assert run_hook("[]").returncode == 2
    assert run_hook({"tool_name": "Bash", "tool_input": None}).returncode == 2
    assert run_hook({"tool_name": "Bash", "tool_input": {"command": None}}).returncode == 2
