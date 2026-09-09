# Country release lock guard

## State

Implemented the automatic release lock guard from canonical source
`0ad481ae3e0ead67851018122615e2520a8e019c` (upstream base
`b8ca61a23e1c7ca9f66181dee36d5d8bee89c916`) in a separate worktree.

## Done

- Read repository instructions and PolicyEngine standards/model-development.
- Confirmed versioning bumps the project without refreshing its lock.
- Preserved the original canonical worktree and all package files.
- Added regression tests before the helper; the first run fails because the
  helper does not yet exist. Tests use a genuine two-package uv-generated lock
  with cached PyPI metadata for idna 3.10 and cover artifact provenance,
  committed-file checks, root-only refresh, and exact rollback.
- Implemented the standard-library helper and committed-file mode. Focused tests
  pass, including rollback after partial writes, graph drift, failed checks,
  unexpected check-time writes, and interruptions. Actual uv with cached PyPI
  metadata accepts a root-only bump and rejects a dependency version change.
- A real uv review probe exposed ancestor workspace discovery despite
  `--no-config --no-sources`. Added a failing regression, then rejected parent
  workspaces before invoking uv. All 24 offline tests pass; the online probe is
  separate and currently blocked by registry DNS on this lane.
- Wired the explicit pre-bump check, single existing bump call, isolated
  Towncrier command, guarded refresh, and scoped sentinel commit. PR and Publish
  validate committed locks, with independent model-free guard tests and locked
  model installs. The Python compatibility matrix retains explicit interpreters.
- Validated parsed workflow order and an isolated real versioning sequence.
  Live PyPI access fails DNS; local equivalents use actual Towncrier and uv
  with genuine cached PyPI metadata, not a production registry success receipt.
- Verified all 17,286 protected tracked files are unchanged, including the
  complete country package, project metadata, and production lock. The original
  worktree remains clean at the original canonical commit.

## Next

- Push the reviewed descendant to the existing PR branch and rebind source/tree
  review to the new head.
- Repeat the normal-registry probe with network access and regenerate/review the
  production lock after calculator 1.0.0 is published. Re-run full PR CI and the
  versioning tree gate before release.

The production lock remains pending publication of spm-calculator 1.0.0 to
PyPI. Full PR validation is expected to fail until a real registry lock is
generated and reviewed. Release guard tests must run independently of the model.
