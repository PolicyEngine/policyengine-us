# Progress

## State

Regression tests for issue #9158 are written. The two federal cases are
failing with the unrounded values while the state override case passes.

## Done

- Read `CLAUDE.md`, `CONTRIBUTING.md`, and the relevant PolicyEngine development
  skills.
- Verified that `upstream/main` is the maintained base and that
  `origin/master` is stale.
- Created branch `fix-snap-min-allotment-rounding-9158` in an isolated worktree.
- Confirmed that the federal result is calculated before DC, Maryland, and New
  Jersey overrides.
- Added cases on both sides of the FY2026 October COLA boundary and a New Jersey
  override case.
- Captured the expected failures: `$23.36` instead of `$23` before the COLA and
  `$23.84` instead of `$24` after it; 9 other cases, including New Jersey,
  passed.

## Next

- Implement federal whole-dollar rounding before state overrides.
- Run focused checks and document the result.
