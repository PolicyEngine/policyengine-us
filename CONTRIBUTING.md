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

### Certificate trust updates

Use uv 0.13.4 or newer and synchronize the patched dependency lock with
`uv sync --locked --extra dev`. Native HTTPS clients such as hf-xet also use
the operating system's certificate store. On Debian or Ubuntu, update it with:

```bash
sudo apt-get update
sudo apt-get install --only-upgrade --yes ca-certificates
```

Use the equivalent certificate-store update for other Linux distributions;
on macOS, install the relevant operating system security updates. Restart
running Python processes and notebook kernels after updating both dependency
and system trust stores. CI updates and verifies the Linux system store before
running model jobs.

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

## Source conflicts

When sources conflict, PolicyEngine US follows these principles (2026-10-20):

- **Statute first.** When a statute conflicts with a form, instructions, a manual or stated agency practice, follow the statute. Forms and instructions fill gaps where the statute is silent.
- **Regulations are law.** A Treasury regulation binds until a court sets it aside, so the statute-first rule doesn't override it. A regulation that flatly contradicts its statute isn't followed automatically: it goes to the project lead, who decides it case by case, and the ruling is recorded in the register.
- **The agency breaks true ties.** Where the text and the canons don't settle a reading, follow the administering agency's reading, so the model matches what households receive.
- **Canons:** definitions control; one meaning per section; no double deduction without a clear statement; specific over general; read timing rules so statutory deadlines can be met; and the operative words govern over form shortcuts.

Every such conflict belongs in the register that PolicyEngine shares with Axiom: `known-source-conflicts.yaml` in [rulespec-us](https://github.com/TheAxiomFoundation/rulespec-us). That repository's `tools/README.md` defines its fields, under "Source-conflict register". When a PR takes such a reading, or finds one already in the code, the conflict goes into the register in four steps, in this order. One PR can't do them all: the guard below rejects a marker unless the pinned copy of the register lists the marker's file under its entry's `implementations`, and the register pins an implementation only to a commit reachable from `main`, which a ruling PR's commits aren't until it merges (and a squash merge never makes the PR's own commits reachable).

1. **The ruling PR records the conflict in `source_conflicts/candidates.yaml`**: its `id`, `program`, `question`, `years`, at least two `sources`, `readings`, `pe_us` (`follows`, `code`, `prs`) and `state`. If the backlog already lists the conflict, it updates that item instead. If the pinned copy already holds the conflict, it adds no item, because the guard fails a registered id. It adds no marker. It also adds what step 2 pins to a commit on `main`: the YAML test cases for its reading and, if the Axiom corpus lacks a source's text, a capture under `source_conflicts/sources/`. You can also add the entry to rulespec-us now, listing the open PR under `proposed`, if every text it cites is in the corpus or captured on `main` already.
2. **After the ruling PR merges, add or complete the entry in rulespec-us.**
   - Give each source's text and its kind (statute, regulation, form, instructions, manual, guidance, agency practice, ...). Cite a text the corpus lacks under `pending_texts`, pinned to its capture's commit on `main`.
   - Give the alternatives, each with an id, and the years.
   - Add an implementation for each file here that holds a deciding line (the candidate's `pe_us.code` can list more): `repo: PolicyEngine/policyengine-us`, the commit on `main` that merged the ruling PR (its squash commit, for a squash merge), the path, `cites_entry: false` (the file doesn't name the global id yet; `verify` reads the file's text, so a `# Candidate: <id>` comment counts), `follows` (what the code does), and `adopts` with a `basis` (the reading it intends, and why). If step 1 listed the PR under `proposed`, move that row to `implementations`.
   - Add the YAML test cases that pin each reading, by commit, path and case name. Pin only commits on `main`: the register records shipped code.
   - Describe correspondence with an agency in `unpublished_sources`. Never quote it or name the person.
3. **Once that entry is on rulespec-us `main`, a follow-up PR here marks the deciding line and refreshes the pin.**
   - Mark the deciding line in each variable or parameter file the entry lists under `implementations`: `# Source conflict <jurisdiction>:<id>`, for example `# Source conflict us-hi:claim-of-right-deduction-floor`.
   - Refresh the pinned copy: `python scripts/update_source_conflicts.py --commit <rulespec-us commit>`.
   - Delete the item from `source_conflicts/candidates.yaml` if it was there. The guard fails a candidate whose id is already in the pinned copy, so the deletion goes in the same PR as the refresh.
   - Delete the file's line from `KNOWN_UNMARKED` in `policyengine_us/tests/code_health/test_source_conflicts.py` if it has one. A valid marker exempts the file from the ratchet, so the guard fails a leftover line.
4. **After the follow-up merges, finish the entry in rulespec-us**: re-pin each implementation to the follow-up's commit on `main` and set `cites_entry: true`. Then refresh the pin here again, so the guard checks that the marker stays.

For code already on `main` that the PR doesn't change, you can skip step 1: pin the implementation to a current `main` commit. The follow-up PR is then the first PolicyEngine US PR, unless step 2 needs a YAML test case or a source capture that isn't on `main` yet. A PR here adds those first.

The marker comes only in the follow-up PR, because the guard rejects a marker whose entry isn't in the pinned copy, or whose entry doesn't list the marker's file under `implementations`. A `proposed` row doesn't count.

`policyengine_us/tests/code_health/test_source_conflicts.py` checks structure, not whether the code follows a statute. It fails when:

- the vendored register (`source_conflicts/known-source-conflicts.yaml`) differs from its pin (`source_conflicts/pin.yaml`: rulespec-us commit and sha256);
- a comment that starts like a marker is not exactly `# Source conflict <jurisdiction>:<id>` alone on its own line. A comment starts like one when it has one or more `#`, then "source conflict" in any case, with any separator or none between the words (a space, hyphen, underscore, dash, dot or zero-width space), followed either by something shaped like a global id (after an optional colon, or after "conflicts") or by no word character and no colon. A file whose comments cannot be read (it doesn't tokenize or parse) fails too;
- a marker names an entry that isn't in the pinned copy, or whose entry doesn't list the file under `implementations`;
- an implementation the register marks `cites_entry: true` is missing here or has lost its marker;
- the count of comments that read like a conflict between sources ("the instructions say", "in practice", "discrepancy", "Source conflict:", ...) changes in a file without a marker. A new file or a higher count means reword a comment that describes no conflict. If it describes a real conflict, keep it, record the conflict as a candidate (step 1) and add or raise the file's `KNOWN_UNMARKED` line in the same PR; the marker in step 3 then exempts the file, and its line comes out. A lower count means lower `KNOWN_UNMARKED`. A file with any valid marker is exempt, so the count doesn't prove every conflict in it is marked;
- a backlog item (`source_conflicts/candidates.yaml`) is malformed, already registered, cites a code path that isn't a file git tracks here (absolute, with `..`, or under a hidden directory such as `.github`), or contains a decision-queue id, a session id, a local path or an email address anywhere in the file: in its raw text, comments and keys included, and in every parsed value and key (escapes, `!!binary`, sets). Homoglyphs, such as a Cyrillic letter in "Source", are not caught; review catches those.

A model that departs from the statute with no official source behind it is a bug, not a source conflict. Fix it, or open an issue.

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
