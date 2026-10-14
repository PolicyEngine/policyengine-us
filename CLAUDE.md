# PolicyEngine US - Development Guide

## ⚠️ MANDATORY FIRST ACTION

At the START of each session, ask the user:

"Would you like to load PolicyEngine development skills for this session?"

**Options to present:**
1. "Yes, load skills" (Recommended) - Load pattern skills for code quality
2. "No, skip" - Proceed without loading skills

**If Option 1 selected, load ALL of these** (from the `policyengine-claude` plugin):
- /complete:policyengine-model-development (variable, parameter, period, and testing patterns)
- /complete:policyengine-standards (code style, formatting, changelog, PR workflow)

If these skills are unavailable (plugin not installed), skip loading and proceed.

---

## Build/Test/Lint Commands
```bash
# Install dependencies
make install
# Alternative installation
pip install -e .[dev]

# Format code
make format  # Runs ruff format

# Run all tests: CI's suites, one bounded subprocess at a time. Never point
# one `policyengine-core test` process at a whole directory tree or hundreds
# of files (see CONTRIBUTING.md, "Memory: running suites locally").
make test

# Run specific test file or directory
pytest policyengine_us/tests/path/to/test_file.py

# Run specific test function
pytest policyengine_us/tests/path/to/test_file.py::test_function_name

# Run specific YAML tests (a few files; for a folder use test_batched.py)
policyengine-core test path/to/test.yaml -c policyengine_us [-v]
uv run python policyengine_us/tests/test_batched.py path/to/folder --mode per-subdir --workers 1

# Run microsimulation test
pytest policyengine_us/tests/microsimulation/test_microsim.py

# Run YAML-specific tests (the suites are sharded; there is no single
# `test-yaml-no-structural` target — see the Makefile for all shards)
make test-yaml-structural            # contrib reforms, non-states
make test-yaml-no-structural-states  # baseline state YAML tests
make test-yaml-no-structural-other-irs   # e.g. IRS shard; other shards: household, ssa-usda, rest-a, rest-b, hhs, ...

# Generate documentation
make documentation
```

## Test design and CI cost

CI time and memory are part of test design. Full model construction, parameter-tree copies, and dataset loading can make a small Python test expensive; test count alone does not measure cost.

- **Use YAML for policy calculations.** Add household examples, thresholds, edge cases, and mixed-household/vectorized cases to the corresponding variable-named YAML files. Do not add a Python test when the existing YAML framework can exercise the same behavior. Avoid generic policy test files such as `regression.yaml` or `vectorized.yaml`.
- **Justify Python coverage.** Use Python for behavior YAML cannot exercise, such as Core integration, data compatibility, simulation APIs, cache/mutation isolation, or tooling. Search existing tests first and explain the distinct failure the new test detects. Do not duplicate a policy formula in Python merely to test it against itself; retain independent reference calculations when they provide meaningful invariant or compatibility coverage.
- **Minimize expensive setup safely.** Use the smallest population, dataset, and set of years that exercise the behavior. Reuse read-only reference models or fixtures where isolation permits. Do not share mutable simulations, reforms, parameter trees, or caches across cases that need independent state, and do not repeatedly construct a full model just to read parameters.
- **Measure simulation-heavy additions.** For new or expanded Python tests that build models, copy policy trees, or load datasets, report before/after elapsed time (including setup) and peak memory where available. Identify the affected CI group and check its existing timing/memory reports. Label local measurements separately from Linux CI results; if resource measurements are unavailable, say so rather than claiming the addition is cheap. Use existing CI artifacts instead of triggering extra full runs solely to benchmark.
- **Keep the existing runner budget.** Do not add jobs, matrix entries, or concurrent heavy processes to absorb test growth without explicit authorization. Assign tests by purpose: simulation/data compatibility belongs with Microsimulation, policy cases with their policy suites, and tooling with code-health checks. Check the Makefile and workflow selectors so moving a file does not omit coverage or accidentally duplicate it within the full suite; selective feedback may intentionally overlap.
- **Preserve memory isolation.** Keep heavy groups in separate, sequential processes on the existing runner. Passing individually does not establish that groups fit together in one process or in parallel. Leave headroom for the runner and future growth; never treat a run just below the memory limit as a safe budget.
- **Do not delete distinct coverage to improve timing.** Preserve essential Core/data compatibility, reform, cache, and isolation tests. Before consolidating tests, compare their setup, operation order, branching, and mutable state as well as their assertions. Identical assertions can protect different behaviors. For changes that only move or delete existing cases, verify the retained contents and collection/routing statically rather than rerunning tests.

## GitHub Workflow
- **Default branch is `main`, NOT `master`.** Base new work on `main`:
  `git fetch upstream main && git checkout -b <branch> upstream/main`. A personal
  fork's `origin/master` is often stale or absent — `git checkout master` can
  silently land you on an ancient commit (e.g. a 1.44.x-era tree missing recent
  contribs), so always branch from `upstream/main` (or `origin/main` when the fork
  is current). Note the upstream remote uses `main` and has no `master` ref.
- Checkout a PR: `gh pr checkout [PR-NUMBER]`
- View PR list: `gh pr list`
- View PR details: `gh pr view [PR-NUMBER]`
- Contributing to PRs:
  - **ALWAYS run `make format` before committing** - this ensures code meets style guidelines and is non-negotiable
  - Use `git push` to push changes to the PR branch

## Changelog
Every PR needs a changelog fragment in `changelog.d/`:
```bash
echo "Description of change." > changelog.d/<branch-name>.<type>.md
```
Types: `added` (minor bump), `changed` (patch), `fixed` (patch), `removed` (minor), `breaking` (major)

The fragment must be a top-level file in `changelog.d/`. Do not create type subdirectories.

Correct:
```text
changelog.d/medicaid-ce-exclusions.added.md
```

Incorrect:
```text
changelog.d/added/medicaid-ce-exclusions.md
changelog.d/medicaid-ce-exclusions.md
```

**DO NOT** edit `CHANGELOG.md` directly or use `changelog_entry.yaml` (deprecated).

## Project Requirements
- Python >= 3.11, < 3.15 (`requires-python` in pyproject.toml; CI smoke-imports the package on 3.11–3.14)
- Follow GitHub Flow with PRs targeting the `main` branch (the default branch is `main`, **not** `master`)
- Every PR needs a changelog fragment in `changelog.d/`
- **ALWAYS run `make format` before every commit** - this is mandatory

## Project-Specific Gotchas
- Unit tests with scalar values can pass while vectorized microsimulation fails
- When implementing a previously empty variable, check for dependent formulas
- When using `defined_for`, ensure it's tested in microsimulation context
- For scale parameters that return integers, avoid using `rate_unit: int` in metadata (use `/1` instead)
- Use `bool` instead of `int` or `/1` in `rate_unit` for scale parameters when appropriate
- Program takeup is assigned during microdata construction, not simulation time
  - Changes to takeup parameters (SNAP, EITC, etc.) have no effect in the web app
  - These parameters should include `economy: false` in their metadata
- **Labor Supply Response & Negative Earnings**: Use `max_(earnings, 0)` to prevent sign flips. Negative total earnings should result in zero labor supply responses.

## Program registry (programs.yaml)
- `policyengine_us/programs.yaml` is the single source of truth for program coverage metadata
- Served via the `/us/metadata` API and consumed by the model coverage page
- **When adding a new program**: add an entry with `id`, `name`, `full_name`, `category`, `agency`, `status`, `coverage`, `variable`, `parameter_prefix`
- **When extending year coverage**: update the entry's year field — most entries use `verified_start_year`, a few use a `verified_years` range (e.g., `"2022-2026"`) — after verifying parameters and tests cover the new year
- **When adding state implementations**: add to `state_implementations` list under the parent federal program
- **Status values**: `complete`, `partial`, `in_progress`. There is no not-started value: when an `in_progress` entry's PR closes unmerged and no code is on main, remove the entry (and its state from `coverage`)
- `policyengine_us/tests/test_programs_registry.py` checks statuses, state codes, and that every `variable` exists and every `parameter_prefix` resolves in the parameter tree. Never add keys to its `KNOWN_UNRESOLVED` list; delete them as entries are fixed
- Keep entries sorted by: Taxes, then Benefits by agency (USDA, HHS, SSA, HUD, FCC, ED, DOE), then State, then Local

## State Program Patterns
- When refactoring federal programs to state-specific implementations:
  - Keep shared federal components if they're from federal regulations (CFR/USC)
  - Check all dependencies before removing variables - use grep to find references
  - Create integration tests to verify the refactoring works correctly
- State programs should be self-contained with their own income calculations and eligibility rules
  - Use state-specific variable names (e.g., `il_tanf_countable_income` not `tanf_countable_income`)

## Regulatory Compliance
- Always cite specific regulation sections in variable reference and documentation
- When implementing complex benefit calculations, document the step-by-step process based on regulations
- Follow the exact order of operations specified in regulations
- Verify behavior at edge cases (income just below/above thresholds, exact boundary conditions)
- Consider real-world examples to validate implementation, including official calculators

## Parameter and variable references
- One `reference` entry per source document; URLs that differ only by `#page=` are one source. Do not split a multi-page table into per-page entries.
- PDF page numbers are file pages (1-indexed), not printed pages.
- One cited page: `#page=57` in the href only, no page in the title.
- Several cited pages: the href opens the first, and the title ends with `#page 72-75` (consecutive) or `#page 29,32-33,36,41` (nonconsecutive). Quote the title, since an unquoted ` #` starts a YAML comment.
- Never put a page list in the href (`#page=1,3,5`).
- Variable reference tuples have no title: put a `# PDF pages 61-62, 67` comment above a multi-page href.

## Axiom Parity (required for policy changes)
- Any PR that adds, updates or fixes policy must also leave the same provision correct in rulespec-us. Put one line in the PR body: `axiom: <legal id> encoded-correct | <rulespec PR> encoded | <rulespec issue> queued | n/a: <reason>`.
- Use `queued` only when the signed encoder is blocked; record the blocker in the issue. Each billed encoder run requires separate approval. A `queued` rulespec-us issue must be dispatch-ready and labelled `pe-parity`. It needs the module path and corpus citation, the verbatim law, the required outputs, and companion tests from the same external source as your YAML tests. See `CONTRIBUTING.md#axiom-parity`.
- Never hand-write RuleSpec. Modules come from the signed encoder.
- If you are an external contributor and cannot complete the Axiom work, use `axiom: needed`; a maintainer will follow up.

## Code Integrity
- **BEFORE DELETING ANY CODE, VERIFY IT IS ACTUALLY UNUSED**
  - Grep for all callers: `grep -r 'name' --include='*.py' | grep -v test | grep -v __pycache__`
  - Code that lives near dead code is not necessarily dead — verify each piece independently
  - Existing tests may bypass the code being removed (e.g. providing a variable as direct input rather than testing its derivation) — passing tests ≠ safe to delete

- **PARTNER API CONTRACT TESTS ARE NOT ORDINARY SNAPSHOTS**
  - Files under `policyengine_us/tests/policy/baseline/partners/**` are API partner contract tests
  - Do not rewrite these expected outputs merely to match changed model behavior or make CI pass
  - If a model change causes partner tests to fail, treat that as a possible partner-facing API change
  - Ziming Hua (@hua7450) approves every edit to files in this folder (Max Ghenis, 2026-10-09). Before editing them, flag the partner-facing risk to the user and put these three questions to Ziming:
    1. Are you sure you want to edit this test file?
    2. Have you notified a team member about this change?
    3. Have you notified the API partner about this change?
  - Ask on the PR that causes the change. Request his review (`gh pr edit <number> --add-reviewer hua7450`) and post a comment (`gh pr comment <number> --body-file <file>`) that names each changed case, its old and new expected values, and the model change and law behind it. If Ziming is the person you are working with, show him the changed cases and ask him directly with the `AskUserQuestion` tool instead; record his answer in a PR comment, which counts as his approval of those edits.
  - Do not edit partner test files until Ziming has answered yes to all three questions, and do not merge a PR that changes them until he has approved a head that contains the edits.
  - Subagents and agent teammates must not edit partner test files. If a subagent or agent teammate finds that an edit is needed, it must stop and report back; the top-level agent takes the three-question gate to Ziming before any edit is made.
  - Before changing expected outputs in this folder, identify the underlying model change and explain the partner impact to Ziming and the user

- **ABSOLUTELY NEVER HARDCODE LOGIC JUST TO PASS SPECIFIC TEST CASES**
  - NEVER add conditional logic that returns fixed values for specific input combinations
  - NEVER use period.start.year or other conditional checks to return hardcoded values for test cases
  - If tests fail, fix the ACTUAL ROOT CAUSE, not the symptom

- When dealing with regulatory examples:
  - Use period-appropriate parameter values
  - Document any special time-period specific logic in BOTH code comments and variable documentation
  - Focus on preserving the calculation PROCESS rather than just matching specific OUTCOMES

## Code Coverage Exclusions
Use `# pragma: no cover` **only** for code that cannot be tested in unit tests:

**Allowed:**
1. Microsim-specific branches: `simulation.is_over_dataset`, `simulation.has_axes`
2. Behavioral response code with simulation branching: `simulation.get_branch()`, `simulation.baseline`

**NOT allowed:**
- Code that simply lacks tests (write tests instead)
- Complex logic that seems hard to test (find a way)
- Edge cases or error handling (these should be tested)

## Parameter Validation Gotchas
- When using `breakdown` metadata in parameters, avoid using variable references for integer values. Use Python expressions like `range(1, 5)`.
- The parameter validation system has issues with certain structures:
  - Using boolean keys (`True`/`False`) as parameter names can cause validation errors
  - Using integer output variables in breakdown metadata can cause errors
- To fix validation issues:
  - Split complex parameters into separate, simpler parameter files
  - Use string names instead of boolean keys
  - See [GitHub issue #346](https://github.com/PolicyEngine/policyengine-core/issues/346)

## Entity Structures
- **Marital Units**:
  - Include exactly 1 person (if unmarried) or 2 people (if married)
  - Do NOT include children or dependents
  - `marital_unit.nb_persons()` will return 1 or 2, never more

- **SSI Income Attribution**:
  - For married couples where both are SSI-eligible: combined income is attributed to each spouse via `ssi_marital_earned_income` and `ssi_marital_unearned_income`

- **SSI Spousal Deeming**:
  - Only applies when one spouse is eligible and the other is ineligible
