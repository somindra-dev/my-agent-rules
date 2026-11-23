# Testing rules (read before writing or changing tests)

- Tests are hermetic: no network, no writes to tracked files.
- Write temporary files under pytest's `tmp_path`, never next to the code.
- If a guard test fails, fix your change. Never weaken a guard.
