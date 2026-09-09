# Release lock guard

The automatic versioning job checks the committed `pyproject.toml` and `uv.lock`
before changing either file. It runs the existing `bump_version.py` exactly once,
builds the changelog with isolated PyPI tooling, and calls
`python .github/release_lock.py --refresh` before the `Update PolicyEngine US`
commit. That commit stages the version, lock, changelog, and consumed fragments.

The guard validates the root package and every dependency source. Registry
packages must use `https://pypi.org/simple`; every listed sdist and wheel must
have a SHA-256 hash and an HTTPS artifact URL on `files.pythonhosted.org`.
A PyPI source label does not make a file, local path, or custom artifact URL
acceptable. Project source overrides, workspaces, and direct requirements are
also rejected, including ancestor workspaces that could redirect uv to another
lock. uv runs without inherited `UV_*`/`PIP_*` overrides or discovered
configuration and uses the standard PyPI registry.

`--committed` requires both project and lock files to match their tracked HEAD
contents, validates their semantics, and runs an actual `uv lock --check`.
The default check supports inspecting an uncommitted candidate, but release CI
uses `--committed`. Neither check repairs a stale lock.

`--refresh` is only for the automatic root version bump. It runs uv to refresh
and check the lock, preserving the complete reviewed dependency graph and all
lock metadata except the root package version. Any dependency, artifact,
constraint, marker, or other semantic change fails the step and restores the
exact previous lock bytes. A uv failure also restores those bytes. Solver
upgrades that change the graph fail closed and require a separate lock review.
The failed workflow cannot reach the automatic commit.

Pull request model jobs depend on `ReleaseLock`. Sentinel push model jobs have
the same prerequisite, and `Publish` checks its own committed checkout again
before installation or build. Model environments use locked synchronization;
subsequent commands use that environment without synchronizing again.

`ReleaseLockTests` has no dependency on a model job or the country lock check.
It uses only the Python standard library and uv, so it can test the guard while
the country dependency registry is incomplete:

```sh
python -m unittest discover -s .github/tests -p test_release_lock.py -v
RELEASE_LOCK_REAL_UV=1 python -m unittest discover -s .github/tests -p test_release_lock.py -v
```

The opt-in probe creates an isolated, minimal project with a standard PyPI
dependency and exercises actual uv locking. CI enables it. These commands do not
install or import the country model.

For the SPM integration, the committed country lock is intentionally still
blocked until `spm-calculator==1.0.0` is available on PyPI and a production
registry lock is regenerated and reviewed separately. A stale root version or
older calculator resolution must fail the full PR and publication gates.
Passing guard tests does not clear that release prerequisite. Do not use local
wheel links or edit lock fields to manufacture a passing lock; the automatic
root-version refresh is not a general dependency update command.
