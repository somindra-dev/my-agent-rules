#!/usr/bin/env python3
"""Claude Code PreToolUse hook: refuse force-pushes.

Claude Code sends one JSON object on stdin, for example
  {"tool_name": "Bash", "tool_input": {"command": "git push --force"}}
Exit 0 = let the tool run. Exit 2 = block it; stderr goes back to the agent.
"""
import json
import shlex
import sys

SEPARATORS = {";", "&&", "||", "|", "&", "(", ")"}
FORCE_FLAGS = {"--force", "--force-with-lease", "--force-if-includes", "--mirror"}


def segments(command):
    """Split a shell line into simple commands: 'a && b; c' -> [[a], [b], [c]]."""
    lex = shlex.shlex(command, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    out, cur = [], []
    for tok in lex:
        if tok in SEPARATORS:
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(tok)
    if cur:
        out.append(cur)
    return out


def is_force_push(tokens):
    if "git" not in tokens:
        return False
    rest = tokens[tokens.index("git") + 1:]
    if "push" not in rest:
        return False
    for a in rest[rest.index("push") + 1:]:
        if a in FORCE_FLAGS or a.startswith("--force-with-lease="):
            return True
        if a.startswith("-") and not a.startswith("--") and "f" in a[1:]:
            return True  # -f, -fu, -uf
        if a.startswith("+"):
            return True  # git push origin +main (forced refspec)
    return False


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("not a JSON object")
        if event.get("tool_name") != "Bash":
            return 0
        command = (event.get("tool_input") or {}).get("command")
        if not isinstance(command, str):
            raise ValueError("no command text")
        parts = segments(command)  # unbalanced quotes raise ValueError
    except Exception as e:  # anything we cannot read: block (fail closed)
        print(f"hook: could not read the tool call ({e}); blocking to be safe",
              file=sys.stderr)
        return 2
    if any(is_force_push(p) for p in parts):
        print("Blocked by hook: force-push is forbidden (rule 1 in CLAUDE.md). "
              "Push a new commit instead.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
