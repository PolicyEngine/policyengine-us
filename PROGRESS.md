# PR B progress — CPUC housing subsidy source + dataset/default/batch guards

Branch: `max/cpuc-housing-and-guards-20260914` (from `upstream/main`, 2.1.0).
Source review: `rollout/fable-continuation-20260911/out/astra-review-country-201.md`.

## State

All four items implemented, reviewed, and pushed.
Draft PR: https://github.com/PolicyEngine/policyengine-us/pull/9464
(head `max/cpuc-housing-and-guards-20260914`, base `main`). Remaining: CI green.

## Done

1. **CPUC CARE/FERA countable income** (Astra P1 #1) —
   `gov/states/ca/cpuc/income_sources.yaml` now counts `housing_assistance`
   instead of `spm_unit_capped_housing_subsidy`.
   - Source verified by fetching PG&E Form 01-9077 (Rev. 6.26) and the CPUC
     tariff sheet (Revised Cal. P.U.C. Sheet No. 61313-E) and reading both:
     the footnote enumerates "housing and military subsidies" among the
     revenues that count, and the form carries no netting, cap, tenant-share
     or poverty-measurement language anywhere (grep-verified). The dead
     `bha.berkeleyca.gov` mirror reference was replaced by PG&E's own URL.
   - Reproduced the defect and the fix on an assisted LA renter (earnings
     $40,700, assistance $23,790): countable income was $40,700 national /
     $41,010.88 county and `ca_care_eligible` flipped True→False; it is now
     $64,490 under national, county and no SPM configuration alike, and
     computes with no county input.
   - Tests: two parametrised geography-independence cases plus a non-vacuity
     case in `tests/unit/test_spm_integration_contract.py` (all three fail on
     the old parameter), and two YAML cases in
     `tests/policy/baseline/gov/states/ca/cpuc/ca_cpuc_countable_income.yaml`.
   - Partner fixtures `partners/analytics_coverage/edge_cases/state/ca/{care,
     fera}.yaml` pass unchanged and were not edited.
2. **Dataset guard aliases** (Astra P2 #6) — `DERIVED_POVERTY_OUTPUTS` beside
   the calculator contract in `spm.py`; a dataset storing `in_poverty`,
   `in_deep_poverty`, `deep_poverty_line`, `deep_poverty_gap` or
   `person_in_poverty` is refused, with a closure test.
3. **Default dataset hash** (Astra P2 #8) — `DEFAULT_DATASET_SHA256` beside the
   URI in `system.py`, checked after resolution for the country default only,
   memoised on (path, size, mtime). Tested with a monkeypatched resolver.
4. **Batch runner exit status** (Astra P2 #7) — the child's exit status decides
   a batch; exit 5 is a failure here (with the divergence from
   `run_selective_tests.py` documented in `batch_status`); `.yml` is
   enumerated alongside `.yaml`. Tests in
   `tests/code_health/test_batched_exit_status.py`, driving real subprocesses.

## Suites run (all exit 0)

- `tests/core` + `tests/unit` + `tests/code_health`: 429 passed.
- CA CPUC YAML + partner CA `care`/`fera`: 96 passed; partner fixtures untouched.
- `policy/baseline/gov/states` in 16 batches: 17 batches, 3,322 files.
- Partner YAML target, all five invocations.
- `policy/baseline/household`, `tests/variables`.
- `policy/contrib/congress` per-subdir, `policy/reform` per-file.
- `make format` clean.
- The certified default build's sha256 verified against the real cached 830 MB
  H5: matches `6496cc43...`.
- Microsimulation impact of the CPUC change, measured over the certified build
  (2026, weighted, CA), with the parameter file swapped on disk between three
  separate processes: `housing_assistance` and `spm_unit_capped_housing_subsidy`
  give an identical `ca_care_income_eligible` of 2,712,528 and mean CA countable
  income of $209,072 vs $209,062. Removing the entry entirely gives 2,743,814.
  So the valuation is immaterial in microsimulation - the certified build
  supplies `receives_housing_assistance` and
  `takes_up_housing_assistance_if_eligible` as inputs, so take-up is not
  imputed there, and the SPM cap seldom binds for genuinely assisted units. The
  household/API path is where the change bites, because take-up defaults true.
  This does not reproduce the review's reported 2,948,108 -> 2,917,330; that
  delta (-30,778) is close in magnitude to this branch's entry-vs-no-entry
  figure (+31,286), but I did not establish what was measured there.

## Not fixed (reported, out of scope)

- Astra P1 #2/#3 and P2 #4/#5 (shared-policy mutation, clone `calc` routing,
  Entity registry rebinding, shared parameter trace caches) belong to PR A /
  policyengine-core, not this branch.
- The CPUC ESA Policy & Procedures Manual §2.2.2 excludes housing subsidies
  from countable income, footnoted to D.14-08-030 OP 40. Its own scope line
  reads "the ESA Program", and OP 40 itself could not be retrieved, so whether
  the exclusion reaches CARE is unresolved. This branch keeps the form's
  treatment (count them) and only corrects how they are valued.

## Review findings addressed (adversarial pass, 2026-09-14)

- The batch runner's monitoring loop was unbounded in both revisions: its
  30-minute budget sat below the loop, where the child had already exited, so
  the wait it guarded returned instantly and never fired. Reading the status
  from the runner rather than terminating a second after the summary also left
  pytest's session-finish window unbounded. Both are enforced inside the loop
  now (`BATCH_TIMEOUT_SECONDS`, `MARKER_GRACE_SECONDS`), with an A/B showing
  the previous revision still running after 40s where this one returns.
- `batch_status`'s docstring claimed pytest exit 2 prints no summary count. It
  does: under policyengine-core's argv, a session whose second test raises
  KeyboardInterrupt exits 2 beneath "1 passed in 0.10s" (measured), which the
  old parse also read as success. Corrected, and it is now the clearest
  example of the defect.
- `_static_variable_reads` in the poverty closure test discarded any variable
  whose class body held no direct entity call, which dropped 884 of the
  system's 6,173 variables - including `poverty_line`, written as
  `adds = ["spm_unit_spm_threshold"]` with no formula at all. The closure was
  therefore blind to the idiom the next alias would most likely use. The scan
  now trusts a formula-less variable's `adds`/`subtracts` and the
  name-listing helpers, covering 5,665 variables; the closure still passes, so
  the rejection set is closed under the stronger scan too.
