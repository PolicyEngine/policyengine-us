# Release lock rehearsal — progress

Branch `max/release-lock-rehearsal-20260911`, stacked on `max/release-lock-uv-toolchain-20260911`
(PR #9444, head a6aef60a, still open on 2026-09-11).

## State

Implementation, tests, docs and changelog are committed and verified locally. An adversarial
review workflow is running over the five dimensions (correctness, bypass, tests, CI, docs).
Remaining: act on confirmed findings, drop this file, push, open the draft PR.

## Done

- `.github/release_lock.py`: `--rehearse`, `bumped_project`, `require_unchanged_checkout`,
  `rehearse_release_lock`, CLI wiring (commit 2dc2f0c9).
- `.github/workflows/pr.yaml`: `Rehearse the release version refresh` step in `ReleaseLock`
  (commit 7e4dbd78).
- `.github/tests/test_release_lock.py`: `RehearsalTests`, `RehearsalCommandTests`, and a real-uv
  rehearsal probe (commit 2dc2f0c9).
- `.github/release-lock.md` and `docs/spm.md`: pinned-uv regeneration command, `--rehearse`
  description, stale spm-calculator paragraphs replaced (commit 409cc58c).
- `changelog.d/release-lock-rehearsal.added.md`.
- Verification transcript in the scratchpad `verification.txt`: 33 unit tests pass with and
  without `RELEASE_LOCK_REAL_UV=1`; `--rehearse` exits 0 on this branch's lock under uv 0.12.13
  and 2 on the pre-#9444 lock, where the plain `uv lock --check` still exits 0.

## Next

1. Resolve confirmed review findings.
2. Drop PROGRESS.md, as the previous lanes in this repo did.
3. `git push upstream max/release-lock-rehearsal-20260911`, open the draft PR against `main`.
