"""Compatibility ingress and complete, source-safe simulation snapshots.

Initial ingress moves legacy benefit inputs to their pure reported sources.
A later public write overrides its period and refreshes its automatic source.
An explicitly supplied reported source retains precedence.
"""

import json
from contextvars import ContextVar
from functools import wraps
from pathlib import Path

from policyengine_core.holders.helpers import get_stored_input
from policyengine_core.periods import period as to_period
from policyengine_core.simulations.simulation import NpEncoder

from policyengine_us.tools.period_branch import delete_input_values


SOCIAL_SECURITY_COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)
_REPORTED_COMPONENTS = tuple(f"{name}_reported" for name in SOCIAL_SECURITY_COMPONENTS)


_initial_social_security_ingress = ContextVar(
    "initial_social_security_ingress", default=False
)
_initial_social_security_writes = ContextVar(
    "initial_social_security_writes", default=None
)
_reloaded_social_security_provenance = ContextVar(
    "reloaded_social_security_provenance", default=None
)
_DUMP_PROVENANCE_FILE = "social_security_input_provenance.json"
_PROVENANCE = "_social_security_input_provenance"
_AUTOMATIC_INPUTS = "_social_security_automatic_reported_inputs"


def _recorded_input_location(
    simulation, name, period, *, branch_names=None, include_unrecorded=False
):
    """Locate a supplied input, or optionally a legacy nonderived cache seed.

    Sequence stamps distinguish automatic sources from explicit replacements
    even when the caller writes exactly the same amount.
    """
    holder = simulation.get_holder(name)
    period = holder._storage_period(period)
    input_keys = getattr(simulation, "_user_input_keys", ())
    if branch_names is None:
        branch_names = simulation._get_visible_branch_names()
    for branch_name in branch_names:
        key = (name, branch_name, period)
        for storage_name, storage, separator in (
            ("memory", holder._memory_storage, ":"),
            ("disk", holder._disk_storage, "_"),
        ):
            if storage is None:
                continue
            recorded = key in input_keys and holder._stores_user_input(
                period, branch_name, storage_name
            )
            if recorded or (
                include_unrecorded
                and storage.has(period, branch_name)
                and not storage.is_derived(period, branch_name)
            ):
                sequence = storage._sequence_numbers.get(
                    f"{branch_name}{separator}{period}"
                )
                return key, (storage_name, sequence)
    return None


def _is_automatic_reported_input(simulation, name, period, *, branch_names=None):
    location = _recorded_input_location(
        simulation, name, period, branch_names=branch_names, include_unrecorded=True
    )
    return location is not None and location[1] in getattr(
        simulation, _AUTOMATIC_INPUTS, {}
    ).get(location[0], ())


def _mark_automatic_reported_input(simulation, name, period, *, branch_name=None):
    location = _recorded_input_location(
        simulation,
        name,
        period,
        branch_names=None if branch_name is None else (branch_name,),
        include_unrecorded=True,
    )
    if location is not None:
        # Core clones simulation attributes shallowly. Never mutate a shared
        # provenance dictionary: each write belongs to this simulation alone.
        automatic = dict(getattr(simulation, _AUTOMATIC_INPUTS, {}))
        # A raw memory mirror can temporarily hide a surviving disk input.
        # Keep each tier's origin so dropping that mirror reveals the original
        # automatic disk source, rather than turning it into an explicit twin.
        stamps = automatic.get(location[0], ())
        automatic[location[0]] = frozenset(
            stamp for stamp in stamps if stamp[0] != location[1][0]
        ) | {location[1]}
        setattr(simulation, _AUTOMATIC_INPUTS, automatic)


def _automatic_reported_metadata(simulation, *, exported_periods=None):
    automatic = {}
    for public_name in SOCIAL_SECURITY_COMPONENTS:
        name = f"{public_name}_reported"
        # Dumping iterates this dictionary. Inspect existing holders without
        # creating missing twins while Core is iterating over their values.
        holder = simulation.persons._holders.get(name)
        if holder is None:
            continue
        for period in holder.get_input_periods(simulation.branch_name):
            if (
                exported_periods is not None
                and (name, str(period)) not in exported_periods
            ):
                continue
            if _is_automatic_reported_input(simulation, name, period):
                automatic.setdefault(name, []).append(str(period))
    return {"version": 1, "automatic_reported": automatic} if automatic else None


def _restore_automatic_reported_metadata(simulation, metadata):
    if metadata is None:
        return
    if not isinstance(metadata, dict) or metadata.get("version") != 1:
        raise ValueError("Unsupported Social Security input provenance version")
    automatic = metadata.get("automatic_reported", {})
    if not isinstance(automatic, dict):
        raise ValueError("Social Security input provenance must contain a mapping")
    for name, periods in automatic.items():
        if name not in _REPORTED_COMPONENTS or not isinstance(periods, list):
            raise ValueError("Invalid automatic Social Security reported input")
        for period in periods:
            _mark_automatic_reported_input(simulation, name, to_period(period))


def install_social_security_input_compatibility():
    """Extend Core's ingress routes only for systems opting into this policy.

    Core's entity builder writes holders directly, and its variable-level
    ``set_input`` handler runs only for mismatched period units. Builder
    and dataset adapters migrate initial sources. Holder-level interception
    preserves subsequent public overrides from every supported input route:
    simulation setters, direct holder writes, and custom period helpers.
    Nonderived cache seeds retain Core's carryover semantics without becoming
    registered inputs; calculated (derived) caches never synchronize.
    """
    from policyengine_core.simulations import Simulation as CoreSimulation
    from policyengine_core.simulations.simulation_builder import SimulationBuilder
    from policyengine_core.holders import Holder

    def tracks_public_input(holder):
        simulation = getattr(holder, "simulation", None)
        return holder.variable.name in SOCIAL_SECURITY_COMPONENTS and getattr(
            getattr(simulation, "tax_benefit_system", None),
            "_social_security_input_compatibility",
            False,
        )

    def synchronize_public_input(holder, period, branch_name, *, is_input):
        simulation = holder.simulation
        variable_name = holder.variable.name
        period = holder._storage_period(period)
        reported_name = f"{variable_name}_reported"
        reported_holder = simulation.get_holder(reported_name)
        readable_branches = reported_holder._readable_branches(branch_name)
        reported_location = _recorded_input_location(
            simulation,
            reported_name,
            period,
            branch_names=readable_branches,
            include_unrecorded=True,
        )
        if reported_location is None or _is_automatic_reported_input(
            simulation, reported_name, period, branch_names=readable_branches
        ):
            supplied_value = (
                get_stored_input(holder, period, branch_name)
                if is_input
                else holder._get_array_from_storage(period, branch_name)
            )
            if supplied_value is not None:
                if is_input:
                    reported_holder.set_input(
                        period, supplied_value.copy(), branch_name
                    )
                else:
                    # Core also uprates from legacy, nonderived cache stores.
                    # Mirror their source semantics without promoting them to
                    # replayable/exported inputs. Calculated caches never enter.
                    reported_holder._set(
                        period, supplied_value.copy(), branch_name, is_input=False
                    )
                _mark_automatic_reported_input(
                    simulation, reported_name, period, branch_name=branch_name
                )
        if not is_input:
            return
        # Core clones share this legacy list. Replace it privately so a
        # later override is extracted without changing the source clone.
        simulation.input_variables = list(
            dict.fromkeys(
                [
                    *getattr(simulation, "input_variables", ()),
                    variable_name,
                    reported_name,
                ]
            )
        )

    original_store = Holder._set
    if not getattr(original_store, "_social_security_compatibility", False):

        @wraps(original_store)
        def store_input(
            holder,
            period,
            value,
            branch_name="default",
            validate_nan=False,
            derived=False,
            is_input=None,
            sequence_number=None,
        ):
            track_source = not derived and tracks_public_input(holder)
            # Mirror Core's classification and effective branch, including
            # restore contexts and custom handlers that store before raising.
            contexts = (
                getattr(holder.simulation, "_user_input_contexts", None)
                if track_source
                else None
            )
            effective_input = bool(contexts) if is_input is None else is_input
            stored_branch = (
                contexts[-1]
                if effective_input and contexts and branch_name == "default"
                else branch_name
            )
            result = original_store(
                holder,
                period,
                value,
                branch_name,
                validate_nan=validate_nan,
                derived=derived,
                is_input=is_input,
                sequence_number=sequence_number,
            )
            loading_writes = _initial_social_security_writes.get()
            if track_source and effective_input and loading_writes is not None:
                loading_writes.setdefault(holder.simulation, {}).setdefault(
                    holder.variable.name, set()
                ).add(holder._storage_period(period))
            # Initial registered inputs wait until every explicit twin is
            # loaded. Raw cache seeds never enter that migration, so mirror
            # them immediately without making either value a supplied input.
            if track_source and (
                not _initial_social_security_ingress.get() or not effective_input
            ):
                synchronize_public_input(
                    holder, period, stored_branch, is_input=effective_input
                )
            return result

        store_input._social_security_compatibility = True
        Holder._set = store_input

    original_dataset_build = CoreSimulation.build_from_dataset
    if not getattr(original_dataset_build, "_social_security_compatibility", False):

        @wraps(original_dataset_build)
        def build_from_dataset(simulation):
            if not getattr(
                simulation.tax_benefit_system,
                "_social_security_input_compatibility",
                False,
            ):
                return original_dataset_build(simulation)
            token = _initial_social_security_ingress.set(True)
            writes = _initial_social_security_writes.get()
            if writes is None:
                writes = {}
            writes_token = _initial_social_security_writes.set(writes)
            try:
                result = original_dataset_build(simulation)
            finally:
                _initial_social_security_writes.reset(writes_token)
                _initial_social_security_ingress.reset(token)
            # Raw Core simulations use this loader without either country
            # constructor or an entity/variable builder. Migrate before Core
            # creates its reform baseline, exactly as for situation ingress.
            migrate_social_security_inputs(
                simulation, loaded_public_inputs=writes.get(simulation, {})
            )
            reloaded = _reloaded_social_security_provenance.get()
            if reloaded is not None and reloaded[0] is simulation:
                _restore_automatic_reported_metadata(simulation, reloaded[1])
            return result

        build_from_dataset._social_security_compatibility = True
        CoreSimulation.build_from_dataset = build_from_dataset

    original_subsample = CoreSimulation.subsample
    if not getattr(original_subsample, "_social_security_compatibility", False):

        @wraps(original_subsample)
        def subsample(simulation, *args, **kwargs):
            if not getattr(
                simulation.tax_benefit_system,
                "_social_security_input_compatibility",
                False,
            ):
                return original_subsample(simulation, *args, **kwargs)
            # Restore stamps during dataset rebuilding, before Core replays
            # inputs and clones the rebuilt reform baseline.
            token = _reloaded_social_security_provenance.set(
                (simulation, _automatic_reported_metadata(simulation))
            )
            try:
                return original_subsample(simulation, *args, **kwargs)
            finally:
                _reloaded_social_security_provenance.reset(token)

        subsample._social_security_compatibility = True
        CoreSimulation.subsample = subsample

    from policyengine_core.tools import simulation_dumper

    original_dump_holder = simulation_dumper._dump_holder
    if not getattr(original_dump_holder, "_social_security_compatibility", False):

        @wraps(original_dump_holder)
        def dump_holder(holder, directory):
            result = original_dump_holder(holder, directory)
            simulation = holder.simulation
            name = holder.variable.name
            if name in _REPORTED_COMPONENTS and getattr(
                simulation.tax_benefit_system,
                "_social_security_input_compatibility",
                False,
            ):
                exported_periods = {
                    (name, str(period)) for period in holder.get_known_periods()
                }
                metadata = _automatic_reported_metadata(
                    simulation, exported_periods=exported_periods
                )
                if metadata is not None:
                    path = Path(directory) / name / _DUMP_PROVENANCE_FILE
                    path.write_text(json.dumps(metadata))
            return result

        dump_holder._social_security_compatibility = True
        simulation_dumper._dump_holder = dump_holder

    original_restore_holder = simulation_dumper._restore_holder
    if not getattr(original_restore_holder, "_social_security_compatibility", False):

        @wraps(original_restore_holder)
        def restore_holder(
            simulation, variable, directory, inputs=False, calculated_number=None
        ):
            if not getattr(
                simulation.tax_benefit_system,
                "_social_security_input_compatibility",
                False,
            ):
                return original_restore_holder(
                    simulation, variable, directory, inputs, calculated_number
                )
            if not inputs and not getattr(
                simulation, "_social_security_dump_inputs_restored", False
            ):
                # Core finishes the input pass before restoring any calculated
                # arrays. Load all twins first, so directory order cannot turn
                # an explicit twin into an automatic source or vice versa.
                migrate_social_security_inputs(simulation)
                for name in _REPORTED_COMPONENTS:
                    path = Path(directory) / name / _DUMP_PROVENANCE_FILE
                    if path.exists():
                        _restore_automatic_reported_metadata(
                            simulation, json.loads(path.read_text())
                        )
                simulation._social_security_dump_inputs_restored = True
            token = _initial_social_security_ingress.set(True)
            # Nested dict/entity/variable builders form one loading operation.
            # Record actual stores, after period helpers have split them, so a
            # builder on an existing simulation refreshes only its new inputs.
            writes = _initial_social_security_writes.get()
            if writes is None:
                writes = {}
            writes_token = _initial_social_security_writes.set(writes)
            try:
                return original_restore_holder(
                    simulation, variable, directory, inputs, calculated_number
                )
            finally:
                _initial_social_security_writes.reset(writes_token)
                _initial_social_security_ingress.reset(token)

        restore_holder._social_security_compatibility = True
        simulation_dumper._restore_holder = restore_holder

    original_extract = CoreSimulation.extract_person
    if not getattr(original_extract, "_social_security_compatibility", False):

        @wraps(original_extract)
        def extract_person(simulation, index=0, exclude_entities=("state",)):
            payload = original_extract(simulation, index, exclude_entities)
            if not getattr(
                simulation.tax_benefit_system,
                "_social_security_input_compatibility",
                False,
            ):
                return payload
            people = payload.get(simulation.persons.entity.plural, {})
            benefit_inputs = {
                name: {
                    str(period): value
                    for period in simulation._get_set_input_periods(name)
                    if (value := simulation._get_recorded_input_array(name, period))
                    is not None
                }
                for name in (*SOCIAL_SECURITY_COMPONENTS, *_REPORTED_COMPONENTS)
            }
            for person_name, person in people.items():
                # Core names extracted people by their original zero-based
                # index plus one, even when extracting a later household.
                person_index = (
                    int(person_name.removeprefix(f"{simulation.persons.entity.key}_"))
                    - 1
                )
                for name, values in benefit_inputs.items():
                    # Core exports its first known period, which may be a
                    # formula cache rather than the later public override.
                    # Keep every actual benefit input and its source history
                    # together, without converting calculated values to inputs.
                    if values:
                        person[name] = {
                            period: float(value[person_index])
                            for period, value in values.items()
                        }
                    else:
                        person.pop(name, None)
            exported_periods = {
                (name, str(period))
                for person in people.values()
                for name, values in person.items()
                if name in _REPORTED_COMPONENTS
                for period in values
            }
            metadata = _automatic_reported_metadata(
                simulation, exported_periods=exported_periods
            )
            if metadata is not None:
                payload[_PROVENANCE] = metadata
            return payload

        extract_person._social_security_compatibility = True
        CoreSimulation.extract_person = extract_person

    original_invalidate = CoreSimulation._invalidate_all_caches
    if not getattr(original_invalidate, "_social_security_compatibility", False):

        @wraps(original_invalidate)
        def invalidate_all_caches(simulation):
            automatic = []
            if getattr(
                simulation.tax_benefit_system,
                "_social_security_input_compatibility",
                False,
            ):
                for key, stamps in getattr(simulation, _AUTOMATIC_INPUTS, {}).items():
                    name, branch_name, period = key
                    location = _recorded_input_location(
                        simulation, name, period, branch_names=(branch_name,)
                    )
                    if location is not None and location[1] in stamps:
                        automatic.append(key)
            result = original_invalidate(simulation)
            # Core replay assigns new store sequence numbers. Replaying an
            # automatic source does not turn it into an explicit caller input.
            for name, branch_name, period in automatic:
                _mark_automatic_reported_input(
                    simulation, name, period, branch_name=branch_name
                )
            return result

        invalidate_all_caches._social_security_compatibility = True
        CoreSimulation._invalidate_all_caches = invalidate_all_caches

    def wrap_builder(original_build):
        @wraps(original_build)
        def build(builder, tax_benefit_system, input_dict, simulation=None):
            if not getattr(
                tax_benefit_system, "_social_security_input_compatibility", False
            ):
                return original_build(
                    builder, tax_benefit_system, input_dict, simulation
                )
            metadata = input_dict.get(_PROVENANCE)
            if _PROVENANCE in input_dict:
                input_dict = {
                    name: values
                    for name, values in input_dict.items()
                    if name != _PROVENANCE
                }
            token = _initial_social_security_ingress.set(True)
            try:
                result = original_build(
                    builder, tax_benefit_system, input_dict, simulation
                )
            finally:
                _initial_social_security_ingress.reset(token)
            # Only build_from_dict rebuilds Core's legacy extraction list.
            # Direct entity/variable builders need the same recorded inputs,
            # including non-benefit sources and exact both-name overrides.
            visible_branches = result._get_visible_branch_names()
            recorded_names = {
                name
                for name, branch_name, _ in result._user_input_keys
                if branch_name in visible_branches
            }
            result.input_variables = list(
                dict.fromkeys(
                    [
                        *getattr(result, "input_variables", []),
                        *sorted(
                            name
                            for name in recorded_names
                            if result._get_set_input_periods(name)
                        ),
                    ]
                )
            )
            migrate_social_security_inputs(
                result, loaded_public_inputs=writes.get(result, {})
            )
            _restore_automatic_reported_metadata(result, metadata)
            return result

        build._social_security_compatibility = True
        return build

    for method_name in (
        "build_from_dict",
        "build_from_entities",
        "build_from_variables",
    ):
        original_build = getattr(SimulationBuilder, method_name)
        if not getattr(original_build, "_social_security_compatibility", False):
            setattr(SimulationBuilder, method_name, wrap_builder(original_build))

    from policyengine_us.tools.social_security_periods import (
        install_social_security_period_compatibility,
    )

    install_social_security_period_compatibility()


def migrate_social_security_inputs(
    simulation, *, include_baseline=True, loaded_public_inputs=None
):
    """Move legacy component inputs, period by period, into pure sources.

    An explicit twin in the same visible period keeps its priority. Automatic
    twins refresh for public inputs stored by this loading operation. Earlier
    public overrides are not initial inputs merely because another builder is
    run on the same simulation. Without a loading record, migrate only legacy
    public inputs with no twin. Recorded-input helpers exclude formula caches
    and honor visible branch precedence.
    """
    visible_branches = simulation._get_visible_branch_names()
    migrated = set()
    for public_name in SOCIAL_SECURITY_COMPONENTS:
        reported_name = f"{public_name}_reported"
        holder = simulation.get_holder(public_name)
        # Snapshot before deleting: deleting a multi-year period also deletes
        # contained supplied periods, including a shorter legacy source whose
        # lexical sort order happens to place it after the longer period.
        sources = {}
        for period in simulation._get_set_input_periods(public_name):
            location = _recorded_input_location(
                simulation, reported_name, period, include_unrecorded=True
            )
            if location is not None and (
                not _is_automatic_reported_input(simulation, reported_name, period)
                or loaded_public_inputs is None
                or period not in loaded_public_inputs.get(public_name, ())
            ):
                continue
            value = simulation._get_recorded_input_array(public_name, period)
            if value is not None:
                sources[period] = value.copy()
        if not sources:
            continue
        retained_overrides = []
        for name, branch_name, period in tuple(simulation._user_input_keys):
            if (
                name != public_name
                or branch_name not in visible_branches
                or period in sources
            ):
                continue
            for storage_name, storage in (
                ("memory", holder._memory_storage),
                ("disk", holder._disk_storage),
            ):
                if holder._stores_user_input(period, branch_name, storage_name):
                    retained_overrides.append(
                        (branch_name, period, storage.get(period, branch_name).copy())
                    )
                    break
        for period, value in sources.items():
            simulation.set_input(reported_name, period, value.copy())
            _mark_automatic_reported_input(simulation, reported_name, period)
        for period in sources:
            for branch_name in visible_branches:
                delete_input_values(holder, period, branch_name)
        # Keep exact-period both-name overrides even inside a migrated longer
        # source period. Restore each original branch slot through set_input,
        # preserving its input classification and ordinary replay bookkeeping.
        for branch_name, period, value in retained_overrides:
            if not holder._stores_user_input(period, branch_name):
                holder.set_input(period, value, branch_name)
        migrated.add(public_name)

    # Core's legacy extraction reads this runtime list, which was assembled
    # before migration. Retain public names only where actual overrides remain.
    runtime_inputs = []
    for name in getattr(simulation, "input_variables", []):
        if name not in migrated or simulation._get_set_input_periods(name):
            runtime_inputs.append(name)
        if name in migrated:
            runtime_inputs.append(f"{name}_reported")
    for public_name in SOCIAL_SECURITY_COMPONENTS:
        reported_name = f"{public_name}_reported"
        if simulation._get_set_input_periods(reported_name):
            runtime_inputs.append(reported_name)
    simulation.input_variables = list(dict.fromkeys(runtime_inputs))
    # Core creates this clone during super().__init__, before either PE-US
    # wrapper reaches migration. Its copied public sources otherwise override
    # formulas in the supplied year and disappear from the uprating route in
    # later years. Each branch needs its own source/input-key migration.
    baseline = getattr(simulation, "baseline", None)
    if include_baseline and baseline is not None and baseline is not simulation:
        migrate_social_security_inputs(baseline, include_baseline=False)
    return migrated


def export_source_inputs(simulation):
    """Export all supplied periods, separating pure sources and final overrides.

    The JSON-compatible payload preserves entity memberships and every recorded
    pure-input period, including selectors, dates, worker links and earnings
    histories. Supplied formula-variable inputs have their own ``overrides``
    payload; calculated results never become sources. Only the current branch
    and its visible ancestors are exported, using their normal precedence.

    This is the complete-history alternative to Core's legacy ``extract_person``
    API, which retains all supplied periods only for benefit components and their
    reported twins. Export the desired small simulation or household; this
    helper deliberately does not materialize a population dataset.
    """
    names = {
        key: [str(name) for name in population.ids]
        for key, population in simulation.populations.items()
    }
    sources = {}
    for key, population in simulation.populations.items():
        entity = population.entity
        sources[entity.plural] = {name: {} for name in names[key]}
        if not entity.is_person:
            # All PE-US group entities use the unbounded member role.
            for person_index, group_index in enumerate(population.members_entity_id):
                group = sources[entity.plural][names[key][int(group_index)]]
                group.setdefault("members", []).append(names["person"][person_index])

    overrides = {}
    for name, variable in simulation.tax_benefit_system.variables.items():
        periods = simulation._get_set_input_periods(name)
        if not periods:
            continue
        for period in periods:
            values = simulation._get_recorded_input_array(name, period)
            if values is None:
                continue
            if hasattr(values, "decode_to_str"):
                values = values.decode_to_str()
            if variable.is_input_variable():
                entity = variable.entity
                for index, entity_name in enumerate(names[entity.key]):
                    source = sources[entity.plural][entity_name]
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
    """Reload a complete source snapshot, then restore its final overrides.

    Pass the desired ``tax_benefit_system`` or ``reform`` through keyword
    arguments. Loading overrides after construction preserves a public-only
    final override instead of treating it as a legacy reported source.
    """
    from policyengine_us import Simulation

    if payload.get("version") != 1:
        raise ValueError("Unsupported source-input snapshot version")
    for period_name in ("default_input_period", "default_calculation_period"):
        simulation_kwargs.setdefault(period_name, payload[period_name])
    metadata = payload.get(_PROVENANCE)
    sources = payload["sources"]
    if metadata is not None:
        # Restore before Core creates a reform baseline, so that clone also
        # knows which twins came from legacy public inputs.
        sources = {**sources, _PROVENANCE: metadata}
    simulation = Simulation(situation=sources, **simulation_kwargs)
    _restore_automatic_reported_metadata(simulation, metadata)
    for name, periods in payload["overrides"].items():
        for period, values in periods.items():
            simulation.set_input(name, period, values)
    simulation.input_variables = list(
        dict.fromkeys([*simulation.input_variables, *payload["overrides"]])
    )
    return simulation
