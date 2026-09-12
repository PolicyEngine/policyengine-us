# Release lock rehearsal — progress

Branch `max/release-lock-rehearsal-20260911`, stacked on `max/release-lock-uv-toolchain-20260911`
(PR #9444, head a6aef60a, still open on 2026-09-11).

## State

Closing the gap #9444 left: PR CI runs `uv lock --check`, which accepts a lock written by a
different uv, so a contributor can regenerate `uv.lock` with any uv, pass CI, and break the next
`Update versioning` run on main. Add a PR-time rehearsal of the release refresh.

## Done

- Read `.github/release_lock.py`, `.github/bump_version.py`, `.github/tests/test_release_lock.py`,
  the three workflows, `.github/release-lock.md`, `docs/spm.md`.
- Probe: `uv lock` succeeds on a directory holding only copied `pyproject.toml` and `uv.lock`
  (no package sources, no README); the root metadata is static, so uv never builds the project.
  The only line that changes is the root version.

## Next

1. `--rehearse` mode in `.github/release_lock.py`.
2. `Rehearse the release version refresh` step in the `ReleaseLock` job of `.github/workflows/pr.yaml`.
3. Unit tests in `.github/tests/test_release_lock.py`, including the real-uv probe.
4. Refresh `.github/release-lock.md` and `docs/spm.md`.
5. Changelog fragment.
6. Local verification with uv 0.12.13, including the failing pre-#9444 lock.
7. Push to `upstream`, open a draft PR.
