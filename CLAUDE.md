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

# Run all tests
make test

# Run specific test file or directory
pytest policyengine_us/tests/path/to/test_file.py

# Run specific test function
pytest policyengine_us/tests/path/to/test_file.py::test_function_name

# Run specific YAML tests
policyengine-core test path/to/tests -c policyengine_us [-v]

# Run microsimulation test
pytest policyengine_us/tests/microsimulation/test_microsim.py

# Run YAML-specific tests
make test-yaml-structural
make test-yaml-no-structural

# Generate documentation
make documentation
```

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
- Python >= 3.11, < 3.15
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
- **When extending year coverage**: update `verified_years` (e.g., `"2022-2026"`) after verifying parameters and tests cover the new year
- **When adding state implementations**: add to `state_implementations` list under the parent federal program
- **Status values**: `complete`, `partial`, `in_progress`
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

## Code Integrity
- **BEFORE DELETING ANY CODE, VERIFY IT IS ACTUALLY UNUSED**
  - Grep for all callers: `grep -r 'name' --include='*.py' | grep -v test | grep -v __pycache__`
  - Code that lives near dead code is not necessarily dead — verify each piece independently
  - Existing tests may bypass the code being removed (e.g. providing a variable as direct input rather than testing its derivation) — passing tests ≠ safe to delete

- **PARTNER API CONTRACT TESTS ARE NOT ORDINARY SNAPSHOTS**
  - Files under `policyengine_us/tests/policy/baseline/partners/**` are API partner contract tests
  - Do not rewrite these expected outputs merely to match changed model behavior or make CI pass
  - If a model change causes partner tests to fail, treat that as a possible partner-facing API change
  - Before editing files in this folder, flag the partner-facing risk to the user and use the `AskUserQuestion` tool to ask these three questions in a single call:
    1. Are you sure you want to edit this test file?
    2. Have you notified a team member about this change?
    3. Have you notified the API partner about this change?
  - Subagents and team members must not edit partner test files. If a subagent or team member finds that an edit is needed, it must stop and report back; the top-level agent runs the three-question gate with the user before any edit is made.
  - Before changing expected outputs in this folder, identify the underlying model change and explain the partner impact to the user

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
