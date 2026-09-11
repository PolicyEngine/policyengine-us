# Fable review fixes on PR #9428 (country 2.0.0)

Branch `max/spm-canonical-final-20260909`, base `main` = d8fb269b, review head
f12188229bb1f006c73c864c2a6b191f4e1513d0.

## State

All five review items are addressed in code. One item is blocked on a human
gate (below). CI-equivalent suites are being run locally the way `.github/
workflows/pr.yaml` runs them.

Verified before editing:

- Worktree HEAD and `upstream/max/spm-canonical-final-20260909` both at f1218822.
- The Populace tag in `DEFAULT_DATASET` is published. One real download
  (`HF_HUB_OFFLINE` unset) resolves the default URI to a file whose sha256 is
  `6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84`, matching
  the published H5 hash. Its `household.county_fips` column holds five-digit
  strings and its `person` table carries `is_spm_independent_minor_role`. The
  default-dataset tests stay real, with no skip guard.
- CI on f1218822 failed seven jobs, not the two the review predicted: Rest (the
  60-minute timeout), Microsimulation, Household API Partners, Baseline
  household, Baseline contrib-hhs, Baseline states-shard-2, and Contrib congress
  (exit 143, runner shutdown during batch 6 - infrastructure, no assertion).

## Done

1. **High 2** - `share_spm_policy` in `policyengine_us/spm.py`: an ordinary
   household simulation now shares the shipped parameter tree and variable
   objects and keeps only its receipts and variable registry private. 20
   sequential single-household simulations plus `household_net_income`: 109.8s
   before, 5.9s after, 6.1s at `main`. This is also why the Rest job timed out.
2. **High 1** - microsimulation tests realigned to the population input
   contract; the legacy policyengine-us-data CPS files are asserted to fail
   closed, and the shipped build carries the society-wide coverage. Five more
   YAML files repaired with the zero-housing-subsidy input this PR already uses.
3. **Lows** - country-level errors for an absent county (naming the two fixes a
   caller has) and for an unresolved dataset build id (naming the URI).
4. **Medium 5** - the absent-county message names the exact caller fix.

## Blocked

`policyengine_us/tests/policy/baseline/partners/analytics_coverage/edge_cases/
state/ca/{care,fera}.yaml` fail with SPM_GEOGRAPHY_REQUIRED. CA CPUC countable
income includes `spm_unit_capped_housing_subsidy`, and both fixtures name their
county as `county_str: LOS_ANGELES_COUNTY_CA`, which the model never converts to
`county_fips`. Editing a partner contract fixture needs the three-question
`AskUserQuestion` gate in CLAUDE.md, which a non-interactive session cannot run,
so these two files are untouched and reported for root's decision.

## Next

- Finish the local CI-equivalent runs and record exact commands and exit codes.
- Write the corrected PR body to the rollout out/ path (root edits GitHub).
- Push and watch `gh pr checks 9428`.
