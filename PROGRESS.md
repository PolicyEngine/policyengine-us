# Parent-id Medicaid MAGI implementation

## State

In progress on `medicaid-magi-parent-ids`, based on `1ca1d4eec`.
Worktree: `/Users/maxghenis/PolicyEngine/_worktrees/policyengine-us-parent-ids`.
Offline execution: no fetch, install, push, or GitHub commands.

## Done

- Read `CLAUDE.md`, `CONTRIBUTING.md`, `AGENTS.md`, `Makefile`, and `pyproject.toml`.
- Verified the existing branch/base and ready Python, pytest, YAML runner, and Ruff executables.
- Confirmed the changelog convention: top-level `changelog.d/<branch>.fixed.md`.
- Selected `REPORT.md` as the final output file because no `-o` path was provided.
- The linked issue and external contribution guide are unavailable under the offline constraint; implementation follows the detailed assignment and locally available references.
- Skipped the repository's initial skills question because the lane explicitly prohibits questions.

## Next

1. Capture existing Medicaid income and demographic behavior and add new regression fixtures.
2. Implement household-scoped parent links with unchanged all-zero fallback paths.
3. Run focused tests and broader Medicaid, CHIP, and demographic suites; review edge cases.
4. Commit implementation and verification progress, write uncommitted `PR_BODY.md`, and finalize `REPORT.md`.

## Verification

- `git status --short --branch`: exit 0; branch `medicaid-magi-parent-ids`; only pre-existing untracked `.venv-install.log`.
- `git log -1 --oneline`: exit 0; `1ca1d4eec Update PolicyEngine US`.
- `.venv/bin/uv` is absent. Run both Makefile format operations directly with `.venv/bin/ruff format .` and `.venv/bin/ruff check .`, per the offline override.
