# my-agent-rules

A tiny Python project to practise agent rules.
Run the tests with `pytest -q`.

## Golden rules (never break these)
1. Never force-push. Never push to `main`; open a pull request.
   Why: a force-push deletes other people's commits, and `main` is what we ship.
2. Never create `v*` tags. Why: a tag starts a release.
3. Tests never use the network and never change tracked files.
   Why: a test that downloads data can silently rewrite files.
4. Never run `rm -rf`. Delete single files by name.
   Why: one wrong path deletes the whole repo.
5. Never edit `.claude/` without asking. Why: it holds the guards.

## Where to read more (open only when you work in that area)
- `docs/claude/testing.md`: before writing or changing tests.
