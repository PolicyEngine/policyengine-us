"""Read-time Social Security sources without automatic reported inputs.

No automatic reported arrays or per-simulation origin maps are created.

Initial public inputs remain supplied Core inputs on reserved source branches
of their public holders. Those branches are invisible to public calculations,
so benefit factors apply in the initial scored year. Later public inputs stay
normal final overrides. Reported holders expose a read-time source view; Core
still performs its own uprating, casting and derived-result caching.

Explicit sources at or before a requested period take precedence. Snapshot
adapters serialize independent public source values and accept older origin
metadata for compatibility; they never serialize new sequence stamps.
"""

import json
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from pathlib import Path

from policyengine_core.data_storage.store_history import next_sequence_number
from policyengine_core.periods import period as to_period
from policyengine_core.simulations.simulation import NpEncoder


SOCIAL_SECURITY_COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)
_REPORTED_COMPONENTS = tuple(f"{name}_reported" for name in SOCIAL_SECURITY_COMPONENTS)
_SOURCE_BRANCH = "__social_security_source__"
_SOURCE_DATA_FILE = "social_security_source_inputs.json"
_LEGACY_DUMP_FILE = "social_security_input_provenance.json"
# Keep the established envelope key so existing complete-snapshot callers
# need not change; version two contains actual source values, never stamps.
_PROVENANCE = "_social_security_input_provenance"

_initial_social_security_ingress = ContextVar("initial_ss_ingress", default=False)
_initial_social_security_writes = ContextVar("initial_ss_writes", default=None)
_reported_request = ContextVar("reported_ss_request", default=None)
_subsampling_social_security_sources = ContextVar(
    "subsampling_ss_sources", default=None
)
_PHYSICAL = {}


@dataclass(frozen=True)
class _Value:
    array: object
    branch: str
    tier: str
    registered: bool


def _enabled(simulation):
    return getattr(
        getattr(simulation, "tax_benefit_system", None),
        "_social_security_input_compatibility",
        False,
    )


def _holder(simulation, name):
    # Never create a holder while Core's dump traverses existing holders.
    persons = getattr(simulation, "persons", None)
    return getattr(persons, "_holders", {}).get(name)


def _branches(simulation, branch_name=None):
    if branch_name is None or branch_name == simulation.branch_name:
        return simulation._get_visible_branch_names()
    return simulation.get_holder(SOCIAL_SECURITY_COMPONENTS[0])._readable_branches(
        branch_name
    )


def _source_branches(simulation, branch_name=None):
    return tuple(
        candidate
        for branch in _branches(simulation, branch_name)
        for candidate in (branch, f"{_SOURCE_BRANCH}{branch}")
    )


def _physical_periods(holder):
    if holder is None:
        return set()
    return {
        period
        for storage in (holder._memory_storage, holder._disk_storage)
        if storage is not None
        for _, period in storage.get_known_branch_periods()
    }


def _physical_value(holder, period, branches, *, registered_only=False):
    """Read supplied values and raw carry seeds, excluding formula caches.

    Core's per-tier input record decides whether an input survives. In
    particular, nonderived memory seeds do not erase a recorded disk input
    from a registered-only snapshot.
    """
    if holder is None:
        return None
    period = holder._storage_period(period)
    keys = getattr(holder.simulation, "_user_input_keys", ())
    for branch in branches:
        for tier, storage in (
            ("memory", holder._memory_storage),
            ("disk", holder._disk_storage),
        ):
            if storage is None or not storage.has(period, branch):
                continue
            if storage.is_derived(period, branch):
                continue
            registered = (
                holder.variable.name,
                branch,
                period,
            ) in keys and holder._stores_user_input(period, branch, tier)
            if not registered_only or registered:
                return _Value(storage.get(period, branch), branch, tier, registered)
    return None


def _explicit_periods(simulation, name, branch_name=None, *, registered_only=False):
    holder = _holder(simulation, name)
    branches = _branches(simulation, branch_name)
    return {
        period
        for period in _physical_periods(holder)
        if _physical_value(holder, period, branches, registered_only=registered_only)
        is not None
    }


def _public_periods(simulation, name, branch_name=None, *, registered_only=False):
    holder = _holder(simulation, name)
    branches = _source_branches(simulation, branch_name)
    return {
        period
        for period in _physical_periods(holder)
        if _physical_value(holder, period, branches, registered_only=registered_only)
        is not None
    }


def _explicit_before(simulation, name, period, branch_name=None):
    period = to_period(period)
    # Core accepts an exact stored compound total before its annual period
    # check, but cannot calculate or uprate another period into that total.
    # An annual explicit source therefore cannot displace an exact multi-year
    # public source. Annual requests retain Core's ordinary source ordering.
    exact_only = period.unit == "year" and period.size > 1
    return any(
        known == period if exact_only else known.start <= period.start
        for known in _explicit_periods(simulation, name, branch_name)
    )


def _allow_fallback(simulation, name, period=None, branch_name=None):
    request = _reported_request.get()
    if request is not None and request[:2] == (simulation, name):
        return request[2]
    return period is None or not _explicit_before(simulation, name, period, branch_name)


def _effective_value(
    simulation, name, period, branch_name=None, *, registered_only=False
):
    explicit = _physical_value(
        _holder(simulation, name),
        period,
        _branches(simulation, branch_name),
        registered_only=registered_only,
    )
    if explicit is not None:
        return explicit, False
    if not _allow_fallback(simulation, name, period, branch_name):
        return None, False
    public = name.removesuffix("_reported")
    source = _physical_value(
        _holder(simulation, public),
        period,
        _source_branches(simulation, branch_name),
        registered_only=registered_only,
    )
    return source, source is not None


def _is_automatic_reported_input(simulation, name, period, *, branch_names=None):
    """Compatibility query computed from surviving sources, without stamps."""
    branch_name = None if branch_names is None else next(iter(branch_names), None)
    _, fallback = _effective_value(simulation, name, period, branch_name)
    return fallback


def _delete_exact(holder, period, branch_name, *, tier=None):
    """Remove one storage slot, preserving compound-period neighbors.

    Core's general delete API also deletes contained periods. Initial routing
    is a representation change and must not delete those other caller inputs.
    """
    period = holder._storage_period(period)
    if tier in (None, "memory"):
        memory = holder._memory_storage
        memory._arrays.pop(f"{branch_name}:{period}", None)
        memory._unmark_dropped_keys()
        memory._stop_sharing_dropped_keys()
        memory._forget_dropped_numbers()
    disk = holder._disk_storage
    if disk is not None and tier in (None, "disk"):
        disk._files.pop(f"{branch_name}_{period}", None)
        disk._forget_dropped_keys()
    recorded = getattr(holder, "_user_input_storage", None)
    if recorded is not None:
        recorded = dict(recorded)
        slot = (branch_name, str(period))
        if tier is None:
            recorded.pop(slot, None)
        elif slot in recorded:
            known_period, locations = recorded[slot]
            recorded[slot] = (known_period, locations - {tier})
        holder._user_input_storage = recorded
    if not holder._stores_user_input(period, branch_name):
        holder.simulation._user_input_keys = {
            key
            for key in getattr(holder.simulation, "_user_input_keys", ())
            if key != (holder.variable.name, branch_name, period)
        }
    holder._evict_fast_cache(period, branch_name)


def _store_source(holder, period, array, branch_name, *, registered=True):
    _PHYSICAL["set"](
        holder,
        period,
        array.copy(),
        branch_name,
        is_input=registered,
    )


def _refresh_input_variables(simulation):
    existing = list(getattr(simulation, "input_variables", ()))
    benefit_names = (*SOCIAL_SECURITY_COMPONENTS, *_REPORTED_COMPONENTS)
    existing = [name for name in existing if name not in benefit_names]
    visible = set(simulation._get_visible_branch_names())
    recorded_names = {
        name
        for name, branch, _ in getattr(simulation, "_user_input_keys", ())
        if branch in visible and name not in benefit_names
    }
    existing.extend(
        name
        for name in sorted(recorded_names)
        if simulation._get_set_input_periods(name)
    )
    for name in benefit_names:
        if simulation._get_set_input_periods(name):
            existing.append(name)
    simulation.input_variables = list(dict.fromkeys(existing))


def migrate_social_security_inputs(
    simulation, *, include_baseline=True, loaded_public_inputs=None
):
    """Route successful initial public stores into invisible source branches.

    A caller-supplied same-period twin keeps the public value as a deliberate
    final override. The independent public source is still preserved, so a
    later raw twin's removal can reveal it again. Composed builders finalize
    only stores belonging to that loading operation.
    """
    moved = set()
    # A loader can fail before Core creates its populations. There are then
    # no successful holder writes to route, including in constructor probes.
    if getattr(simulation, "persons", None) is None:
        return moved
    purged = False
    for name in SOCIAL_SECURITY_COMPONENTS:
        holder = _holder(simulation, name)
        if holder is None:
            continue
        reported = f"{name}_reported"
        for branch in _branches(simulation):
            source_branch = f"{_SOURCE_BRANCH}{branch}"
            for period in tuple(_physical_periods(holder)):
                value = _physical_value(holder, period, (branch,), registered_only=True)
                if value is None:
                    continue
                if loaded_public_inputs is not None:
                    if (name, branch, period) not in loaded_public_inputs:
                        continue
                elif _physical_value(holder, period, (source_branch,)) is not None:
                    # A constructor's second migration must retain later
                    # public overrides and must not reclassify source copies.
                    continue
                explicit = _physical_value(
                    _holder(simulation, reported), period, _branches(simulation)
                )
                # Routing removes an exact public override and exposes its
                # formula. A custom input handler may already have calculated
                # values from that override while the builder was loading.
                simulation._drop_values_that_may_depend_on(name, period)
                if not purged:
                    # Core's dependency drops apply only on branches. A
                    # builder can replace a source on an ordinary simulation
                    # whose base or downstream values are already cached.
                    # Keep raw carry seeds and every supplied input intact.
                    _purge_derived_arrays(simulation)
                    purged = True
                _store_source(holder, period, value.array, source_branch)
                if explicit is None:
                    # A local source must also displace inherited public
                    # final overrides in this simulation's private snapshot.
                    # Retain each ancestor's independent public source for
                    # ordinary branch fallback after a later local raw write.
                    for visible in _branches(simulation):
                        inherited = _physical_value(holder, period, (visible,))
                        if inherited is not None and visible != branch:
                            _store_source(
                                holder,
                                period,
                                inherited.array,
                                f"{_SOURCE_BRANCH}{visible}",
                                registered=inherited.registered,
                            )
                        _delete_exact(holder, period, visible)
                moved.add(name)
    _refresh_input_variables(simulation)
    baseline = getattr(simulation, "baseline", None)
    if include_baseline and baseline is not None and baseline is not simulation:
        migrate_social_security_inputs(baseline, include_baseline=False)
    return moved


def _automatic_reported_metadata(
    simulation, *, exported_periods=None, person_indices=None, include_raw=False
):
    """Serialize source data, not automatic provenance or sequence stamps.

    Physical public values are sufficient to reconstruct the read-time view.
    ``projected_reported`` identifies only the compatibility projections in
    the surrounding payload, so reload does not mistake them for new explicit
    twins. It is derived at export and is never kept on the simulation.
    """
    sources = []
    projected = {}
    for public in SOCIAL_SECURITY_COMPONENTS:
        holder = _holder(simulation, public)
        if holder is None:
            continue
        for kind, branches in (
            ("initial", tuple(f"{_SOURCE_BRANCH}{b}" for b in _branches(simulation))),
            ("override", tuple(_branches(simulation))),
        ):
            for period in _physical_periods(holder):
                value = _physical_value(
                    holder, period, branches, registered_only=not include_raw
                )
                if value is None:
                    continue
                array = value.array
                if person_indices is not None:
                    array = array[person_indices]
                sources.append(
                    {
                        "name": public,
                        "period": str(period),
                        "kind": kind,
                        "values": array,
                        "registered": value.registered,
                    }
                )
        reported = f"{public}_reported"
        for period in _public_periods(simulation, public, registered_only=True):
            if (
                exported_periods is not None
                and (reported, str(period)) not in exported_periods
            ):
                continue
            value, fallback = _effective_value(
                simulation, reported, period, registered_only=True
            )
            if value is not None and fallback:
                projected.setdefault(reported, []).append(str(period))
    if not sources and not projected:
        return None
    return json.loads(
        json.dumps(
            {"version": 2, "public_sources": sources, "projected_reported": projected},
            cls=NpEncoder,
        )
    )


def _restore_automatic_reported_metadata(simulation, metadata, *, dumped=False):
    """Accept old automatic projections; restore new independent public data."""
    if metadata is None:
        return
    if not isinstance(metadata, dict) or metadata.get("version") not in (1, 2):
        raise ValueError("Unsupported Social Security source-data version")
    if metadata["version"] == 1:
        # Older snapshots stored real automatic reported arrays. Move those
        # values into independent public source slots and remove their copies.
        for name, periods in metadata.get("automatic_reported", {}).items():
            if name not in _REPORTED_COMPONENTS or not isinstance(periods, list):
                raise ValueError("Invalid legacy Social Security source data")
            holder = _holder(simulation, name)
            for text in periods:
                period = to_period(text)
                value = _physical_value(holder, period, _branches(simulation))
                if value is None:
                    continue
                source = simulation.get_holder(name.removesuffix("_reported"))
                _store_source(
                    source,
                    period,
                    value.array,
                    f"{_SOURCE_BRANCH}{simulation.branch_name}",
                    registered=value.registered,
                )
                _delete_exact(holder, period, value.branch)
    else:
        for name, periods in metadata.get("projected_reported", {}).items():
            if name not in _REPORTED_COMPONENTS or not isinstance(periods, list):
                raise ValueError("Invalid projected Social Security source")
            holder = _holder(simulation, name)
            if holder is not None:
                for text in periods:
                    for branch in _branches(simulation):
                        _delete_exact(holder, to_period(text), branch)
        import numpy as np

        for entry in metadata.get("public_sources", ()):
            name, kind = entry.get("name"), entry.get("kind")
            if name not in SOCIAL_SECURITY_COMPONENTS or kind not in (
                "initial",
                "override",
            ):
                raise ValueError("Invalid Social Security public source")
            branch = simulation.branch_name
            if kind == "initial":
                branch = f"{_SOURCE_BRANCH}{branch}"
            _store_source(
                simulation.get_holder(name),
                to_period(entry["period"]),
                np.asarray(entry["values"]),
                branch,
                registered=True if dumped else entry.get("registered", True),
            )
    _refresh_input_variables(simulation)


def _select_subsample_sources(simulation, metadata, person_ids):
    """Apply Core's retained person rows to independent public source data.

    Core keeps selected IDs and adjusts weights rather than duplicating rows.
    Using those IDs also follows its entity rebuild when the original IDs are
    nonconsecutive or the retained groups have different original sizes.
    """
    if metadata is None:
        return None
    positions = {person_id: index for index, person_id in enumerate(person_ids)}
    retained = [positions[person_id] for person_id in simulation.persons.ids]
    return {
        **metadata,
        "public_sources": [
            {
                **entry,
                "values": [entry["values"][index] for index in retained],
            }
            for entry in metadata.get("public_sources", ())
        ],
    }


def _purge_derived_arrays(simulation):
    """Discard formula results after benefit sources change.

    Core's general cache drop also removes nonregistered, nonderived carry
    seeds. Those are independent caller values and remain valid here.
    """
    for population in simulation.populations.values():
        for holder in population._holders.values():
            for tier, storage in (
                ("memory", holder._memory_storage),
                ("disk", holder._disk_storage),
            ):
                if storage is None:
                    continue
                for branch, period in tuple(storage.get_known_branch_periods()):
                    if storage.is_derived(period, branch):
                        _delete_exact(holder, period, branch, tier=tier)
    simulation._fast_cache = {}


def install_social_security_input_compatibility():
    from policyengine_core.holders import Holder
    from policyengine_core.simulations import Simulation as CoreSimulation
    from policyengine_core.simulations.simulation_builder import SimulationBuilder
    from policyengine_core.tools import simulation_dumper

    if getattr(Holder.get_array, "_social_security_readtime", False):
        return
    if getattr(Holder._set, "_social_security_compatibility", False):
        raise RuntimeError(
            "Replace eager compatibility before installing read-time hooks"
        )

    _PHYSICAL.update(
        set=Holder._set,
        get_array=Holder.get_array,
        get_known_periods=Holder.get_known_periods,
        get_input_periods=Holder.get_input_periods,
        recorded_periods=CoreSimulation._get_set_input_periods,
        recorded_array=CoreSimulation._get_recorded_input_array,
        calculate=CoreSimulation._calculate,
    )

    @wraps(_PHYSICAL["get_array"])
    def get_array(holder, period, branch_name="default"):
        simulation, name = holder.simulation, holder.variable.name
        if (
            name not in _REPORTED_COMPONENTS
            or not _enabled(simulation)
            or holder.variable.is_neutralized
        ):
            return _PHYSICAL["get_array"](holder, period, branch_name)
        value, fallback = _effective_value(simulation, name, period, branch_name)
        if value is not None:
            if fallback:
                simulation._get_store_history().record_derived(
                    name.removesuffix("_reported"), next_sequence_number()
                )
            return value.array
        return _PHYSICAL["get_array"](holder, period, branch_name)

    get_array._social_security_readtime = True
    Holder.get_array = get_array

    @wraps(_PHYSICAL["get_known_periods"])
    def get_known_periods(holder):
        values = _PHYSICAL["get_known_periods"](holder)
        if holder.variable.name in _REPORTED_COMPONENTS and _enabled(holder.simulation):
            if _allow_fallback(holder.simulation, holder.variable.name):
                values = [
                    *values,
                    *(
                        period
                        for period in _public_periods(
                            holder.simulation,
                            holder.variable.name.removesuffix("_reported"),
                        )
                        if _effective_value(
                            holder.simulation, holder.variable.name, period
                        )[0]
                        is not None
                    ),
                ]
        return list(dict.fromkeys(values))

    Holder.get_known_periods = get_known_periods

    @wraps(_PHYSICAL["get_input_periods"])
    def get_input_periods(holder, branch_name="default"):
        simulation, name = holder.simulation, holder.variable.name
        if name not in _REPORTED_COMPONENTS or not _enabled(simulation):
            return _PHYSICAL["get_input_periods"](holder, branch_name)
        periods = _explicit_periods(simulation, name, branch_name)
        if _allow_fallback(simulation, name, branch_name=branch_name):
            periods |= _public_periods(
                simulation, name.removesuffix("_reported"), branch_name
            )
        return [
            period
            for period in periods
            if _effective_value(simulation, name, period, branch_name)[0] is not None
        ]

    Holder.get_input_periods = get_input_periods

    @wraps(_PHYSICAL["calculate"])
    def calculate(simulation, name, period=None):
        if (
            name not in _REPORTED_COMPONENTS
            or not _enabled(simulation)
            or period is None
        ):
            return _PHYSICAL["calculate"](simulation, name, period)
        token = _reported_request.set(
            (simulation, name, not _explicit_before(simulation, name, period))
        )
        try:
            return _PHYSICAL["calculate"](simulation, name, period)
        finally:
            _reported_request.reset(token)

    CoreSimulation._calculate = calculate

    @wraps(_PHYSICAL["recorded_periods"])
    def recorded_periods(simulation, name):
        periods = set(_PHYSICAL["recorded_periods"](simulation, name))
        if name in _REPORTED_COMPONENTS and _enabled(simulation):
            periods |= _public_periods(
                simulation, name.removesuffix("_reported"), registered_only=True
            )
            periods = {
                period
                for period in periods
                if _effective_value(simulation, name, period, registered_only=True)[0]
                is not None
            }
        return sorted(periods, key=str)

    CoreSimulation._get_set_input_periods = recorded_periods

    @wraps(_PHYSICAL["recorded_array"])
    def recorded_array(simulation, name, period):
        if name not in _REPORTED_COMPONENTS or not _enabled(simulation):
            return _PHYSICAL["recorded_array"](simulation, name, period)
        value, _ = _effective_value(simulation, name, period, registered_only=True)
        return None if value is None else value.array

    CoreSimulation._get_recorded_input_array = recorded_array

    @wraps(_PHYSICAL["set"])
    def store(
        holder,
        period,
        value,
        branch_name="default",
        validate_nan=False,
        derived=False,
        is_input=None,
        sequence_number=None,
    ):
        simulation, name = holder.simulation, holder.variable.name
        tracked = (
            not derived
            and name in (*SOCIAL_SECURITY_COMPONENTS, *_REPORTED_COMPONENTS)
            and _enabled(simulation)
        )
        if tracked:
            public = name.removesuffix("_reported")
            simulation._drop_values_that_may_depend_on(public, period)
            # Component bases and downstream results also depend on the
            # reported source. Core's dependency drops run only on branches,
            # so ordinary simulations need the same derived-only cleanup.
            _purge_derived_arrays(simulation)
        result = _PHYSICAL["set"](
            holder,
            period,
            value,
            branch_name,
            validate_nan=validate_nan,
            derived=derived,
            is_input=is_input,
            sequence_number=sequence_number,
        )
        if tracked:
            contexts = getattr(simulation, "_user_input_contexts", ())
            registered = bool(contexts) if is_input is None else is_input
            effective_branch = (
                contexts[-1]
                if registered and contexts and branch_name == "default"
                else branch_name
            )
            writes = _initial_social_security_writes.get()
            if name in SOCIAL_SECURITY_COMPONENTS and registered and writes is not None:
                writes.setdefault(simulation, set()).add(
                    (name, effective_branch, holder._storage_period(period))
                )
            elif name in SOCIAL_SECURITY_COMPONENTS:
                # One logical public slot has one latest value. Replacing a
                # source on this same branch retires its initial-routing
                # copy; an inherited source on another branch remains a
                # separate parent input, as ordinary Core fallback requires.
                _delete_exact(
                    holder,
                    holder._storage_period(period),
                    f"{_SOURCE_BRANCH}{effective_branch}",
                )
            _refresh_input_variables(simulation)
        return result

    Holder._set = store

    def wrap_loading(original, *, dataset=False):
        @wraps(original)
        def load(first, *args, **kwargs):
            system = (
                first.tax_benefit_system
                if dataset
                else args[0]
                if args
                else kwargs["tax_benefit_system"]
            )
            if not getattr(system, "_social_security_input_compatibility", False):
                return original(first, *args, **kwargs)
            metadata = None
            if not dataset:
                input_dict = args[1] if len(args) > 1 else kwargs["input_dict"]
                metadata = input_dict.get(_PROVENANCE)
                if _PROVENANCE in input_dict:
                    input_dict = {
                        k: v for k, v in input_dict.items() if k != _PROVENANCE
                    }
                    if len(args) > 1:
                        args = (args[0], input_dict, *args[2:])
                    else:
                        kwargs = {**kwargs, "input_dict": input_dict}
            outermost = not _initial_social_security_ingress.get()
            token = _initial_social_security_ingress.set(True)
            writes = _initial_social_security_writes.get()
            if writes is None:
                writes = {}
            writes_token = _initial_social_security_writes.set(writes)
            result = None
            try:
                result = original(first, *args, **kwargs)
                return result
            finally:
                _initial_social_security_writes.reset(writes_token)
                _initial_social_security_ingress.reset(token)
                if outermost:
                    targets = dict(writes)
                    target = first if dataset else result
                    if target is None and not dataset:
                        target = kwargs.get("simulation")
                        if target is None and len(args) > 2:
                            target = args[2]
                    if target is not None:
                        targets.setdefault(target, set())
                    for target, loaded in targets.items():
                        # During routing, projected twins temporarily retain
                        # any both-name public final overrides. Conversion
                        # then replaces those projection arrays with the
                        # independently serialized public source data.
                        migrate_social_security_inputs(
                            target, loaded_public_inputs=loaded
                        )
                        rebuilding = _subsampling_social_security_sources.get()
                        if (
                            dataset
                            and rebuilding is not None
                            and rebuilding[0] is target
                        ):
                            metadata = _select_subsample_sources(
                                target, rebuilding[1], rebuilding[2]
                            )
                        _restore_automatic_reported_metadata(target, metadata)

        return load

    CoreSimulation.build_from_dataset = wrap_loading(
        CoreSimulation.build_from_dataset, dataset=True
    )
    for name in ("build_from_dict", "build_from_entities", "build_from_variables"):
        setattr(SimulationBuilder, name, wrap_loading(getattr(SimulationBuilder, name)))

    original_subsample = CoreSimulation.subsample

    @wraps(original_subsample)
    def subsample(simulation, *args, **kwargs):
        if not _enabled(simulation):
            return original_subsample(simulation, *args, **kwargs)
        token = _subsampling_social_security_sources.set(
            (
                simulation,
                _automatic_reported_metadata(simulation),
                tuple(simulation.persons.ids),
            )
        )
        try:
            return original_subsample(simulation, *args, **kwargs)
        finally:
            _subsampling_social_security_sources.reset(token)

    CoreSimulation.subsample = subsample

    original_extract = CoreSimulation.extract_person

    @wraps(original_extract)
    def extract_person(simulation, index=0, exclude_entities=("state",)):
        payload = original_extract(simulation, index, exclude_entities)
        if not _enabled(simulation):
            return payload
        people = payload.get(simulation.persons.entity.plural, {})
        indices = []
        exported = set()
        for person_name, person in people.items():
            person_index = (
                int(person_name.removeprefix(f"{simulation.persons.entity.key}_")) - 1
            )
            indices.append(person_index)
            for name in (*SOCIAL_SECURITY_COMPONENTS, *_REPORTED_COMPONENTS):
                values = {
                    str(period): float(array[person_index])
                    for period in simulation._get_set_input_periods(name)
                    if (array := simulation._get_recorded_input_array(name, period))
                    is not None
                }
                if values:
                    person[name] = values
                    exported.update((name, period) for period in values)
                else:
                    person.pop(name, None)
        metadata = _automatic_reported_metadata(
            simulation, exported_periods=exported, person_indices=indices
        )
        if metadata is not None:
            payload[_PROVENANCE] = metadata
        return payload

    CoreSimulation.extract_person = extract_person

    original_dump = simulation_dumper._dump_holder

    @wraps(original_dump)
    def dump_holder(holder, directory):
        result = original_dump(holder, directory)
        if not _enabled(holder.simulation):
            return result
        if holder.variable.name in (*SOCIAL_SECURITY_COMPONENTS, *_REPORTED_COMPONENTS):
            # A virtual source need not have a physically visible array.
            # Core creates the directory before discovering that; leave no
            # empty holder folder for its restore parser to misinterpret.
            storage_path = Path(directory) / holder.variable.name
            if storage_path.exists() and not any(storage_path.iterdir()):
                storage_path.rmdir()
        if holder.variable.name in SOCIAL_SECURITY_COMPONENTS:
            metadata = _automatic_reported_metadata(holder.simulation, include_raw=True)
            if metadata is not None:
                # Core enumerates every root entry as a variable to restore.
                # Keep source data inside a valid holder directory, including
                # when all this holder's actual inputs use hidden branches.
                storage_path = Path(directory) / holder.variable.name
                storage_path.mkdir(exist_ok=True)
                (storage_path / _SOURCE_DATA_FILE).write_text(json.dumps(metadata))
        return result

    simulation_dumper._dump_holder = dump_holder
    original_restore = simulation_dumper._restore_holder

    @wraps(original_restore)
    def restore_holder(
        simulation, variable, directory, inputs=False, calculated_number=None
    ):
        if not _enabled(simulation):
            return original_restore(
                simulation, variable, directory, inputs, calculated_number
            )
        if not inputs and not getattr(
            simulation, "_social_security_source_data_restored", False
        ):
            source_path = next(
                (
                    path
                    for name in SOCIAL_SECURITY_COMPONENTS
                    if (path := Path(directory) / name / _SOURCE_DATA_FILE).exists()
                ),
                None,
            )
            if source_path is not None:
                _restore_automatic_reported_metadata(
                    simulation, json.loads(source_path.read_text()), dumped=True
                )
            else:
                for name in _REPORTED_COMPONENTS:
                    path = Path(directory) / name / _LEGACY_DUMP_FILE
                    if path.exists():
                        _restore_automatic_reported_metadata(
                            simulation, json.loads(path.read_text()), dumped=True
                        )
                migrate_social_security_inputs(simulation)
            simulation._social_security_source_data_restored = True
        token = _initial_social_security_ingress.set(True)
        try:
            return original_restore(
                simulation, variable, directory, inputs, calculated_number
            )
        finally:
            _initial_social_security_ingress.reset(token)

    simulation_dumper._restore_holder = restore_holder

    # Core's physical replay/drop/clone methods require no automatic-stamp
    # adapter: the independent public source is a genuine registered input.
    # The complete snapshot entry points below keep their established shape.
    from policyengine_us.tools.social_security_periods import (
        install_social_security_period_compatibility,
    )

    install_social_security_period_compatibility()


def export_source_inputs(simulation):
    """Export all registered source periods and final overrides."""
    names = {
        key: [str(name) for name in population.ids]
        for key, population in simulation.populations.items()
    }
    sources = {}
    for key, population in simulation.populations.items():
        entity = population.entity
        sources[entity.plural] = {name: {} for name in names[key]}
        if not entity.is_person:
            for person_index, group_index in enumerate(population.members_entity_id):
                group = sources[entity.plural][names[key][int(group_index)]]
                group.setdefault("members", []).append(names["person"][person_index])
    overrides = {}
    for name, variable in simulation.tax_benefit_system.variables.items():
        for period in simulation._get_set_input_periods(name):
            values = simulation._get_recorded_input_array(name, period)
            if values is None:
                continue
            if hasattr(values, "decode_to_str"):
                values = values.decode_to_str()
            if variable.is_input_variable():
                for index, entity_name in enumerate(names[variable.entity.key]):
                    source = sources[variable.entity.plural][entity_name]
                    source.setdefault(name, {})[str(period)] = values[index]
            else:
                overrides.setdefault(name, {})[str(period)] = values
    return json.loads(
        json.dumps(
            {
                "version": 1,
                "sources": sources,
                "overrides": overrides,
                _PROVENANCE: _automatic_reported_metadata(simulation),
                "default_input_period": str(simulation.default_input_period),
                "default_calculation_period": str(
                    simulation.default_calculation_period
                ),
            },
            cls=NpEncoder,
        )
    )


def reload_source_inputs(payload, **simulation_kwargs):
    """Reload complete snapshots, including legacy automatic projections."""
    from policyengine_us import Simulation

    if payload.get("version") != 1:
        raise ValueError("Unsupported source-input snapshot version")
    for period_name in ("default_input_period", "default_calculation_period"):
        simulation_kwargs.setdefault(period_name, payload[period_name])
    metadata = payload.get(_PROVENANCE)
    sources = payload["sources"]
    if metadata is not None:
        sources = {**sources, _PROVENANCE: metadata}
    simulation = Simulation(situation=sources, **simulation_kwargs)
    for name, periods in payload["overrides"].items():
        for period, values in periods.items():
            simulation.set_input(name, period, values)
    _refresh_input_variables(simulation)
    return simulation
