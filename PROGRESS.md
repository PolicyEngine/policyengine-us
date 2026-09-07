# Parent-id Medicaid MAGI implementation

## State

Implementation and focused validation complete on `medicaid-magi-parent-ids`, based on `1ca1d4eec`; broader validation remains.
Worktree: `/Users/maxghenis/PolicyEngine/_worktrees/policyengine-us-parent-ids`.
Offline execution: no fetch, install, push, or GitHub commands.

## Done

- Read `CLAUDE.md`, `CONTRIBUTING.md`, `AGENTS.md`, `Makefile`, and `pyproject.toml`.
- Verified the existing branch/base and ready Python, pytest, YAML runner, and Ruff executables.
- Confirmed the changelog convention: top-level `changelog.d/<branch>.fixed.md`.
- Selected `REPORT.md` as the final output file because no `-o` path was provided.
- The linked issue and external contribution guide are unavailable under the offline constraint; implementation follows the detailed assignment and locally available references.
- Skipped the repository's initial skills question because the lane explicitly prohibits questions.
- Added optional parent ID inputs, household-scoped parent lookup and sibling sums, Medicaid relationship branches, and parent-status inference. Mother/father formulas continue to use `is_parent`; breastfeeding remains independent.
- Added nine Medicaid YAML cases, five demographic YAML cases, and two Python tests for mixed households and exact zero/omitted-input equivalence.
- Reproduced the supplied three-generation proxy before changing formulas: children size 10, income $141,848, non-filer rules true, Medicaid eligibility false in Ohio 2026.
- Ran new fixtures against the old formulas: Medicaid 4 failed / 3 passed; demographics 3 failed / 1 passed (expected red evidence preserved under `checkpoints/`).
- Focused final YAML run: 100 passed, exit 0. Python parent-link tests: 2 passed, exit 0.
- Added the top-level fixed changelog fragment. Read-only review found no blocker for valid unique person IDs.

## Next

1. Run all Medicaid, CHIP, and demographic YAML tests and the demographic Python test; add final targeted edge coverage if warranted.
2. Compare selected zero-ID outputs byte-for-byte against the original formulas.
3. Commit verification progress, write uncommitted `PR_BODY.md`, and finalize `REPORT.md`.

## Verification

- `git status --short --branch`: exit 0; branch `medicaid-magi-parent-ids`; only pre-existing untracked `.venv-install.log`.
- `git log -1 --oneline`: exit 0; `1ca1d4eec Update PolicyEngine US`.
- `.venv/bin/uv` is absent. Run both Makefile format operations directly with `.venv/bin/ruff format .` and `.venv/bin/ruff check .`, per the offline override.
- Initial formatter: exit 0 (`3 files reformatted, 6710 files left unchanged`); lint: exit 0 (`All checks passed!`). Restored the formatter's three unrelated Markdown edits before proceeding.
- `.venv/bin/policyengine-core test policyengine_us/tests/policy/baseline/gov/hhs/medicaid/income -c policyengine_us`: exit 0, `38 passed, 1 warning in 25.53s`; `checkpoints/02-baseline-medicaid-income.log`.
- `.venv/bin/policyengine-core test policyengine_us/tests/policy/baseline/gov/hhs/medicaid/income policyengine_us/tests/policy/baseline/household/demographic/person -c policyengine_us`: exit 0, `100 passed, 1 warning in 29.68s`; `checkpoints/03-focused.log`.
- `.venv/bin/pytest policyengine_us/tests/core/test_parent_links.py -q`: exit 0, `2 passed, 1 warning in 1.89s`; `checkpoints/04-parent-links-python.log`.
- Full `make test` is not selected: the tracked test tree has 4,697 files and includes data-dependent microsimulations. Use the assignment's explicit Medicaid/CHIP/demographic alternative (126 pre-existing YAML files, plus the two new files).
