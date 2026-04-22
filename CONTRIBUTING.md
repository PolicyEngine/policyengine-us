# Contributing to policyengine-us

See the [shared PolicyEngine contribution guide](https://github.com/PolicyEngine/.github/blob/main/CONTRIBUTING.md) for cross-repo conventions (towncrier changelog fragments, `uv run`, PR description format, anti-patterns). This file covers policyengine-us specifics.

## Commands

```bash
make install                                         # install deps (uv)
make format                                          # format (required)
make test                                            # full test suite
make test-yaml-structural                            # YAML tests that need microsim
make test-yaml-no-structural                         # YAML tests that don't
uv run policyengine-core test policyengine_us/tests/path/to/test.yaml -c policyengine_us
uv run pytest policyengine_us/tests/path/to/test_file.py::test_name -v
```

Python 3.11–3.14. Default branch: `main`.

## Writing variables and programs

Four types of files usually change together:

| Type                  | Location                                                   |
| --------------------- | ---------------------------------------------------------- |
| YAML unit tests       | `policyengine_us/tests/policy/...`                         |
| Parameter (`.yaml`)   | `policyengine_us/parameters/gov/<agency>/...` (IRS, USDA, HHS, SSA, HUD, ED, DOE, states) |
| Variable (`.py`)      | `policyengine_us/variables/gov/<agency>/...`               |
| Changelog fragment    | `changelog.d/<branch>.<type>.md`                           |

Conventions:

- Write YAML tests **first** (TDD). They fail until the variable formula is in place.
- Use `where(...)`, `max_(...)`, `min_(...)` inside formulas — never Python `if` / `max` / `min`. Vectorisation requires numpy.
- Match the variable file name to the class name (e.g. `my_tax_credit.py` defines `class my_tax_credit(Variable)`).
- Filing-status breakdowns must cover all five statuses: `SINGLE`, `SEPARATE`, `SURVIVING_SPOUSE`, `HEAD_OF_HOUSEHOLD`, `JOINT`. If a source only lists four, treat `SURVIVING_SPOUSE` the same as `JOINT`.
- For scale parameters returning integers, use `/1` in `rate_unit`, not `int`.
- Cite the specific CFR / USC / state-code section in the variable's `reference` field.
- State programs should be self-contained with state-specific variable names (e.g. `il_tanf_countable_income`, not `tanf_countable_income`).

See [CLAUDE.md](./CLAUDE.md) for variable/parameter/period/testing patterns in depth, plus skill references for code style, parameter patterns, and entity structures.

## Program registry

`policyengine_us/programs.yaml` is the single source of truth for program coverage metadata and drives the `/us/metadata` API. When adding a new program, add an entry with `id`, `name`, `full_name`, `category`, `agency`, `status`, `coverage`, `variable`, `parameter_prefix`. When extending year coverage, bump `verified_years` (e.g. `"2022-2026"`) after verifying parameters and tests cover the new year. When adding a state implementation of a federal program, add it to `state_implementations` under the parent federal entry.

## Repo-specific anti-patterns

- **Don't** open PRs from forks — create the branch on upstream (`make push-pr-branch`). Fork PRs can't access repository secrets and CI fails on data-download steps.
- **Don't** hardcode logic just to pass specific test cases. Fix the root cause. No `period.start.year == 2024` conditional returns.
- **Don't** delete code without grepping for callers (`grep -r 'name' --include='*.py' | grep -v test | grep -v __pycache__`). Tests may bypass the code being removed.
- **Don't** modify the `Variable` or `Parameter` base-class contracts without coordinating with `policyengine-core`.
- **Don't** use `# pragma: no cover` for code that simply lacks tests — write tests instead. Valid uses: `simulation.is_over_dataset` / `simulation.has_axes` branches, and `simulation.get_branch()` / `simulation.baseline` in behavioural-response code.

## SSI, marital-unit, and behavioural-response gotchas

- Marital units include exactly 1 person (unmarried) or 2 people (married) — **never** children or dependents. `marital_unit.nb_persons()` returns 1 or 2, never more.
- SSI income attribution for married couples where both are SSI-eligible: combined income is attributed via `ssi_marital_earned_income` / `ssi_marital_unearned_income`.
- SSI spousal deeming applies only when one spouse is eligible and the other is ineligible.
- Labor-supply responses: use `max_(earnings, 0)` to prevent sign flips. Negative total earnings should yield zero LSR.
- Program take-up is assigned during microdata construction, not simulation time. Changes to take-up parameters (SNAP, EITC, etc.) have no effect in the web app; these parameters should include `economy: false` in their metadata.
