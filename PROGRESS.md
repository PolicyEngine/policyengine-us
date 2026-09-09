# Country release lock guard

## State

Implementing the automatic release lock guard from canonical source
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

## Next

- Write failing release guard regressions, including a real uv registry fixture.
- Check the committed lock before bumping; refresh only the root version after
  the existing bump helper; restore lock bytes on errors or dependency drift.
- Validate registry sources and every artifact URL/hash; gate PR and Publish.
- Run focused tests and an isolated real bump/refresh probe, verify unchanged
  package files, and push the resulting descendant to the existing PR branch.

The production lock remains pending publication of spm-calculator 1.0.0 to
PyPI. Full PR validation is expected to fail until a real registry lock is
generated and reviewed. Release guard tests must run independently of the model.
