# Progress

## State

Whole-dollar rounding is implemented at the federal calculation before state
overrides. Focused and full SNAP tests pass. Two partner contract expectations
show the same intentional annual change and are preserved pending the required
user-confirmation gate.

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
- Applied nearest-whole-dollar rounding to the federal minimum allotment before
  the DC, Maryland, and New Jersey override chain.
- Added the required towncrier fix fragment.
- Passed all 11 focused minimum-allotment cases.
- Identified one directly affected annual SNAP expectation: the lawful rounded
  monthly floors sum to `$291` instead of the old unrounded `$288.61`. The same
  case passes at `$288.61` on the clean base.
- Passed all 490 tests in the full SNAP YAML directory.
- Ran the 22 partner files that assert SNAP: 158 cases passed and two contract
  expectations retained the old `$288.61` result instead of the new `$291`.
  No partner file was edited.

## Next

- Complete the required three-question user gate before editing any partner
  contract expectation.
- If authorized, update the two intentional partner outputs and rerun partner
  validation.
