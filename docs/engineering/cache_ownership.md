# Core cache ownership and the US migration

Read this document before changing US simulation branching, policy sharing,
parameter processing, or cache access. Core's
[cache architecture](https://github.com/PolicyEngine/policyengine-core/blob/master/docs/engineering/skills/cache_architecture.md)
defines the shared contracts. The US adapter must use public operations, not
write cache dictionaries, holder storage indexes, or input-provenance sets.

## Required behavior

Type C, parameter-at-date caching, belongs to the policy tree and its revision.
`replace_parameters(tree)` installs a processed or detached tree with a fresh
dated-view cache. `share_parameters_from(system)` deliberately shares the tree
and its cache. Cached views contain no simulation tracer; Core attaches tracing
to the active calculation. US no longer creates per-simulation tracing roots.

Type D separates authoritative supplied inputs from disposable calculation
results. `set_input` and `Holder.set_input` record supplied-input provenance and
invalidate the receiving simulation's results. `delete_arrays` and
`Holder.delete_arrays` update storage and provenance together. Call
`clear_calculated_results()` to keep supplied inputs while discarding results;
do not copy inputs out, clear holder storage, and replay them.

An existing branch keeps its input snapshot after its parent changes. Immutable
array payloads may share memory, but indexes and pending invalidations do not.
Use `get_supplied_input` and `supplied_input_periods` to inspect supplied values.
Call `rebind_tax_benefit_system()` after replacing a simulation's system: Core
rebinds entities and holders and prunes inputs for removed or incompatible
variables without discarding valid retained results. Core also rebinds cloned
method aliases, including `calc` and `df`.
US owns a separate system wrapper per simulation, so it passes
`set_simulation_backreference=True` when rebinding. Core's default leaves a
deliberately shared system's existing simulation reference unchanged.

## Behavior that remains US-owned

US formula branches deliberately share parameter trees until a parameter reform
requires a private tree. `SharedParameterPolicy` retains that copy-on-write
behavior. A parent reform explicitly moves its linked descendants to the new
tree and invalidates their results; it excludes the baseline and independent
policy branches. Changing a child's parameters does not reform its parent.

Branches made without `clone_system=True` also share the variable registry.
A supported variable reform explicitly invalidates and rebinds every member
using that registry, including parents and siblings. This does not update input
snapshots or private registries. Directly mutating a registered variable object
is not a supported replacement for the public reform methods.

Forecast providers and calculation receipts remain simulation-local. The US
adapter also retains period-specific branch naming and reuse: a different
period, override, or parent `input_revision` creates a new comparison branch.
Core advances that revision on supplied-input writes, deletion and pruning,
including holder operations. Clearing calculated results alone does not change
it. This lets formulas use the parent's current inputs without mutating old
named snapshots or scanning every input on each comparison. Override-comparison values
are immutable snapshots, so mutating a caller's array cannot change the branch's
reuse identity. Core's input invalidation
replaces the former country code that inspected and cleared inherited arrays.

`clone_spm_system` still copies actual variable instance state because Core's
variable cloning reconstructs variable classes and does not preserve every
partially defined reform or neutralization. Its entity-copy normalization also
remains. These are model/variable ownership limitations, not cache mutation
APIs; removing them requires a separately tested Core guarantee. Country-owned
forecast and pinned-policy caches are not the YAML runner's Type B cache.

## Three stages and four PRs

1. Release preparatory [Core #599](https://github.com/PolicyEngine/policyengine-core/pull/599),
   including all public APIs and ownership guarantees above. Compatibility
   adapters remain in Core for older country releases only.
2. Release [US #9980](https://github.com/PolicyEngine/policyengine-us/pull/9980)
   and [UK #2176](https://github.com/PolicyEngine/policyengine-uk/pull/2176).
   Both migrate their supported operations now; neither waits for final cleanup
   to stop using cache internals or remove redundant correctness workarounds.
3. Release the separate Core cleanup PR after both country releases. Remove
   compatibility adapters, not the preparatory guarantees.

Before merging the US PR, set `policyengine-core` in `pyproject.toml` to the
actual published preparatory version and regenerate `uv.lock`. No unreleased
version number is assumed here. The current lockfile does not prove readiness
for that release: local qualification uses the editable preparatory Core branch.
Repeat the affected US tests against the published package before release.

## Validation and cost

`tests/core/test_core_cache_contract.py` uses three test variables and a one-person
population to test US/Core integration without constructing the full US model
per case. Existing SPM tests retain full-model coverage of policy sharing,
reform-only inputs, baseline policy, aliases and tracing. Existing override
branch tests retain policy-result comparisons and multi-year coverage.

The new module joins the SPM tests in their existing sequential process on the
Microsimulation runner; the Rest groups exclude it through `REST_SPM_TESTS`. This
migration adds no runner, concurrent heavy process, dataset download, or US
parallel-runner switch. Record local elapsed time and peak memory separately
from Linux CI measurements when qualifying a change.
