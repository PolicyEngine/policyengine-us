# Fable review fixes on PR #9428 (country 2.0.0)

Branch `max/spm-canonical-final-20260909`, base `main`, review head
f12188229bb1f006c73c864c2a6b191f4e1513d0.

## State

All five review items are addressed. Hosted CI on the pushed head is green
except the Household API Partners job, which fails on two partner contract
fixtures that need a human gate this session cannot run.

## Done

1. **High 2 - policy sharing.** `share_spm_policy` in `policyengine_us/spm.py`.
   Three paths held no policy of their own and were deep-cloning the shipped
   system: no reform and no supplied system; a supplied system with no reform
   (the household API's shape, and most of this suite's); and the baseline
   branch core builds for a reform. All three now share the parameter tree and
   variable objects and keep only receipts and variable registration private. A
   supplied system *with* a reform still gets the full clone, because core
   applies the reform set to whatever system it is handed.
   - 20 single-household simulations plus `household_net_income`: 6.14s at main,
     109.81s at the review head, 4.74s now.
   - 174 tests in four `tests/core` files, itemization branching on: 26.12s at
     main, 545.58s at the review head, 26.56s now.
   - `make test-other-python`: 4m37s at main (437 tests), 5m18s now (510).
2. **High 1 - the suite passes.** Microsimulation tests realigned to the
   population input contract; five more YAML files repaired with the
   zero-housing-subsidy input this PR already uses. CI: Rest 22m36s (was a
   60-minute timeout), Microsimulation 8m4s, every Baseline and Contrib shard
   green.
3. **Lows.** Country-level errors for an absent county, naming the two fixes a
   caller has, and for an unresolved dataset build id, naming the URI.
4. **Medium 5.** The absent-county message names the exact caller fix.
5. **Medium 3.** Corrected PR body written to the rollout `out/` path; the PR
   itself is untouched, as instructed.

## Blocked

`tests/policy/baseline/partners/analytics_coverage/edge_cases/state/ca/{care,
fera}.yaml` fail with SPM_GEOGRAPHY_REQUIRED: CA CPUC countable income includes
`spm_unit_capped_housing_subsidy`, and both fixtures name their county as
`county_str`, which the model never converts to `county_fips`. Editing a partner
contract fixture needs the three-question gate in CLAUDE.md, which a
non-interactive session cannot run. A ready patch and a drafted partner notice
already sit at `rollout/fable-continuation-20260911/out/partner-fixtures-county-
fips.patch` and `partner-notice-county-fips.md`; the patch applies cleanly to
this head. Left for root.
