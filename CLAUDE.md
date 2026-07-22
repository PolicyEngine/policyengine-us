# PolicyEngine US - Development Guide

## ⚠️ MANDATORY FIRST ACTION

At the START of each session, ask the user:

"Would you like to load PolicyEngine development skills for this session?"

**Options to present:**
1. "Yes, load skills" (Recommended) - Load pattern skills for code quality
2. "No, skip" - Proceed without loading skills

**If Option 1 selected, load ALL of these:**
- /policyengine-code-style
- /policyengine-parameter-patterns
- /policyengine-period-patterns
- /policyengine-testing-patterns
- /policyengine-variable-patterns

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

**DO NOT** edit `CHANGELOG.md` directly or use `changelog_entry.yaml` (deprecated).

## Project Requirements
- Python >= 3.11, < 3.15
- Follow GitHub Flow with PRs targeting master branch
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

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **policyengine-us** (28974 symbols, 40791 relationships, 119 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/policyengine-us/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/policyengine-us/context` | Codebase overview, check index freshness |
| `gitnexus://repo/policyengine-us/clusters` | All functional areas |
| `gitnexus://repo/policyengine-us/processes` | All execution flows |
| `gitnexus://repo/policyengine-us/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
