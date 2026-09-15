# Second-pass review work on #9467

Working log for the adversarial review at
`rollout/fable-continuation-20260911/out/review-9467.md`. Removed before the
branch is handed back.

## State

All six findings committed, one commit each. Local verification green.

## Done

- F1 full-population housing-allocation probe over the certified default build
  and over `enhanced_cps_2024`, count in the failure message. No guard added.
- F2 `spm-housing-allocation` and `care-housing-income` retyped `changed` and
  rewritten around consequence; `spm-supplied-policy-caches.fixed.md` restored.
- F3 digest and URI recorded in `docs/spm.md` with the date read, pinned by
  `test_documented_default_build_matches_the_shipped_constants`.
- F4 `docs/spm.md` and `.github/release-lock.md` describe the shipped
  calculator range and the published 1.0.0 resolution.
- F5 #9448's two tracer tests fail against #9463's mechanism and are not
  carried; the reason is recorded, and the policy-family docstring corrected.
- F6 the pre-2014 CPUC inclusion names the modelled quantity it counts.

Verification: `ruff format --check .` exit 0, `ruff check .` exit 0,
`pytest tests/core tests/unit tests/code_health` 535 passed,
CPUC + Tlaib YAML 58 passed exit 0, `release_lock.py --committed` exit 0.

## Next

- Push, update the PR body with a second-pass section, poll CI.
- Drop this log before handing the branch back.
