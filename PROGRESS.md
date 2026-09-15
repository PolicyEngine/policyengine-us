# Second-pass review work on #9467

Working log for the adversarial review at
`rollout/fable-continuation-20260911/out/review-9467.md`. Removed before the
branch is handed back.

## State

Six findings, one commit each. F1-F4 and F6 are committed; F5 is written and
waiting on the core suites.

## Done

- F1 full-population housing-allocation probe over the certified default build
  and over `enhanced_cps_2024`, with the overlap count in the failure message.
  No guard added.
- F2 `spm-housing-allocation` and `care-housing-income` retyped `changed` and
  rewritten around consequence; `spm-supplied-policy-caches.fixed.md` restored.
- F3 digest and URI recorded in `docs/spm.md` with the date read, pinned by
  `test_documented_default_build_matches_the_shipped_constants`.
- F4 `docs/spm.md` and `.github/release-lock.md` now describe the shipped
  calculator range and the published 1.0.0 resolution.
- F6 the pre-2014 CPUC inclusion names the modelled quantity it counts, in the
  parameter and in the fragment.

## Next

- F5 commit: #9448's two tracer tests fail against #9463's mechanism and are
  not carried; the reason is recorded in the isolation suite, and the
  policy-family docstring is corrected.
- Fast suites, CPUC/Tlaib YAML, `release_lock.py --committed`, ruff.
- Push, update the PR body, poll CI.
