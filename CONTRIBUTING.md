# Contributing to policyengine-us

See the [shared PolicyEngine contribution guide](https://github.com/PolicyEngine/.github/blob/main/CONTRIBUTING.md) for cross-repo conventions (towncrier changelog fragments, `uv run`, PR description format, anti-patterns). This file covers policyengine-us specifics.

## Commands

```bash
make install                                         # pip install -e .[dev] (CI uses uv sync --extra dev)
make format                                          # format (required)
make test                                            # full test suite
make test-yaml-structural                            # contrib-reform YAML tests, non-states
# The YAML suites are sharded; there is no single test-yaml-no-structural
# target. Examples (see the Makefile for all shards):
make test-yaml-no-structural-states                  # baseline state YAML tests
make test-yaml-no-structural-other-irs               # other shards: household, ssa-usda, rest-a, rest-b, hhs, ...
uv run policyengine-core test policyengine_us/tests/path/to/test.yaml -c policyengine_us
uv run pytest policyengine_us/tests/path/to/test_file.py::test_name -v
```

### Memory: running suites locally

`make test` runs the same suites as CI, one batched subprocess at a time
(`policyengine_us/tests/test_batched.py`). CI sizes those batches to stay
under about 8 GB each on 16 GB runners, so this is the safe way to run
everything on a laptop.

- One area: its `make test-yaml-*` target, or
  `uv run python policyengine_us/tests/test_batched.py <dir> --mode per-subdir --workers 1`.
- A few files: `uv run policyengine-core test <files> -c policyengine_us`.
- Never give one `policyengine-core test` process a whole directory tree or
  hundreds of files. The YAML runner keeps every case's simulation, a full
  copy of the tax-benefit system for each distinct `reforms` /
  dotted-parameter combination (about 1.2 GB each), and a copy of the
  parameter tree for every date a case asked about, all for the life of the
  process. A 1,500-file baseline run reached 118 GB on 2026-10-02.
  PolicyEngine/policyengine-core#569 and #570 (open drafts) would bound
  this; until they are released, keep each process to a bounded batch.
- Run one large suite at a time: don't start several `make test-yaml-*`
  targets, or several `test_batched.py` runs, in parallel.

Python 3.9–3.14 (`requires-python = ">=3.9,<3.15"`; CI smoke-imports on every minor). Default branch: `main`.

## Integration branch pilot

Small independent fixes, especially agent-authored fixes, target `integration`
during this opt-in pilot. Urgent fixes, changes that must publish today, and
changes to CI itself target `main`. A maintainer enables the pilot by creating
`integration` from `main` after the promotion workflow reaches `main`.
The GitHub App installation needs contents, pull requests, and workflows write
permissions for promotion and synchronization ([GitHub App permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)).

Ready PRs into `integration` run three runner jobs: PR validation (`ReleaseLock`),
package and compatibility (`PackageCompatibility`), and selective tests with
coverage (`Quick-Feedback`). Ready PRs into `main`, including promotion PRs, run
the existing full suite of 26 runner jobs. Draft PRs run no jobs for either base.
The release and publishing workflow still runs on pushes to `main`.

The promotion workflow is scheduled every four hours in UTC and also runs
manually. It opens no promotion when `integration` is absent, has no commits
that `main` lacks, or already has an open promotion PR. Otherwise it freezes
the current head on `promote/<UTC timestamp>` and opens a non-draft PR into
`main` listing its member PRs and commits. New fixes on `integration` wait for
the next promotion; the workflow never updates an existing snapshot. The PR
uses the GitHub App token so its CI runs automatically, as described in
[GitHub's workflow trigger documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow#triggering-a-workflow-from-a-workflow).

Merge a successful promotion with a **merge commit**, preserving each fix's
commits and changelog fragments. Do not squash the promotion. The next workflow
tick brings `main`, including the release bot's version bump, back into
`integration` with a clean merge. A merge conflict stops the promotion and emits
a warning; a maintainer resolves the conflict on `integration` before running
the workflow again. A push to `integration` starts no full-suite workflow.

For a red promotion, preserve the failed PR and logs while investigating:

1. In a separate local checkout of the frozen snapshot, reproduce the failure
   with the failing shard's exact command and dependency setup from its workflow.
   Verify that command passes at the promotion's pre-batch `main` commit.
2. Run `git bisect start --first-parent <snapshot-sha> <known-good-main-sha>`
   and `git bisect run <failing-shard-command>`, then `git bisect reset`.
   First-parent history follows the member fixes in their landing order. If the
   result is a merge, inspect the member commits or the synchronization with
   `main` to identify the failing change.
3. Revert the culprit on `integration` (`git revert <sha>`, or
   `git revert -m 1 <sha>` for a member-PR merge), with a changelog fragment.
   Close the failed promotion PR, keeping it as evidence, and run the promotion
   workflow manually to cut a fresh snapshot. Leave the failed snapshot intact.

## Writing variables and programs

Four types of files usually change together:

| Type                  | Location                                                   |
| --------------------- | ---------------------------------------------------------- |
| YAML unit tests       | `policyengine_us/tests/policy/...`                         |
| Parameter (`.yaml`)   | `policyengine_us/parameters/gov/<agency>/...` (IRS, USDA, HHS, SSA, HUD, ED, DOE, states) |
| Variable (`.py`)      | `policyengine_us/variables/gov/<agency>/...`               |
| Changelog fragment    | `changelog.d/<branch>.<type>.md`                           |

Conventions:

- Changelog fragments must be top-level files like `changelog.d/my-change.fixed.md`; do not use `changelog.d/fixed/my-change.md` or omit the type suffix.
- Write YAML tests **first** (TDD). They fail until the variable formula is in place.
- Use `where(...)`, `max_(...)`, `min_(...)` inside formulas — never Python `if` / `max` / `min`. Vectorisation requires numpy.
- Match the variable file name to the class name (e.g. `my_tax_credit.py` defines `class my_tax_credit(Variable)`).
- Filing-status breakdowns must cover all five statuses: `SINGLE`, `SEPARATE`, `SURVIVING_SPOUSE`, `HEAD_OF_HOUSEHOLD`, `JOINT`. If a source only lists four, treat `SURVIVING_SPOUSE` the same as `JOINT`.
- Enum breakdown parameters must be real tables, not single-member tables. If a parameter only applies to one enum member, make it a scalar under a member-specific path instead of using `metadata.breakdown`; for example use `.../income_limit/ny/earned_income.yaml` with `values:` rather than a `state_code` table containing only `NY`.
- For scale parameters returning integers, use `/1` in `rate_unit`, not `int`.
- Cite the specific CFR / USC / state-code section in the variable's `reference` field.
- State programs should be self-contained with state-specific variable names (e.g. `il_tanf_countable_income`, not `tanf_countable_income`).

See [CLAUDE.md](./CLAUDE.md) for variable/parameter/period/testing patterns in depth, plus skill references for code style, parameter patterns, and entity structures.

## Program registry

`policyengine_us/programs.yaml` is the single source of truth for program coverage metadata and drives the `/us/metadata` API. When adding a new program, add an entry with `id`, `name`, `full_name`, `category`, `agency`, `status`, `coverage`, `variable`, `parameter_prefix`. When extending year coverage, bump the entry's year field — most entries use `verified_start_year`; a few use a `verified_years` range (e.g. `"2022-2026"`) — after verifying parameters and tests cover the new year. When adding a state implementation of a federal program, add it to `state_implementations` under the parent federal entry.

## Axiom parity

Every policy change here must also be correct in [rulespec-us](https://github.com/TheAxiomFoundation/rulespec-us). That covers a new program, a parameter or threshold update, an eligibility rule and a bug fix. The shared guide, [Mirror policy changes in Axiom](https://github.com/PolicyEngine/.github/blob/main/CONTRIBUTING.md#mirror-policy-changes-in-axiom), defines the `axiom:` line your PR description needs and what a `queued` issue must contain. US specifics:

- Federal modules live under `us/` (for example `us/statutes/26/32.yaml` for the EITC and `us/policies/irs/rev-proc-2025-32/` for annual IRS amounts). State modules live under `us-<state>/` (for example `us-nj/statutes/54a:4-7.yaml`). Search `main` there before opening a new issue.
- An `encoded-correct` claim names the module and a companion case in its `.test.yaml` that exercises the same situation as your YAML test.
- Use `queued` only when the signed encoder is blocked; record the blocker in the issue. Each billed encoder run requires separate approval. Label `queued` issues `pe-parity`. Reuse your YAML test's external expected values as the companion tests; don't copy values computed by policyengine-us.

## Repo-specific anti-patterns

- Branching on upstream (`git push upstream <branch>`) is preferred when you have write access, but fork PRs are fine here: PR CI needs no repository secrets (the only one, `CODECOV_TOKEN`, uploads with `fail_ci_if_error: false`, and codecov passes tokenless) and downloads no gated data, so fork PRs run the full suite green.
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
