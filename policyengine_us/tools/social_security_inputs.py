"""Compatibility ingress and complete, source-safe simulation snapshots.

Initial ingress moves legacy benefit inputs to their pure reported sources.
A later public write overrides its period and seeds an absent reported source.
"""

import json
from contextvars import ContextVar
from functools import wraps

from policyengine_core.simulations.simulation import NpEncoder

from policyengine_us.tools.period_branch import delete_input_values


SOCIAL_SECURITY_COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)


_initial_social_security_ingress = ContextVar(
    "initial_social_security_ingress", default=False
)


def install_social_security_input_compatibility():
    """Extend Core's ingress routes only for systems opting into this policy.

    Core's entity builder writes holders directly, and its variable-level
    ``set_input`` handler runs only for mismatched period units. A builder
    adapter therefore migrates initial sources, while a simulation adapter
    preserves subsequent public overrides, including on raw Core simulations.
    """
    from policyengine_core.simulations import Simulation as CoreSimulation
    from policyengine_core.simulations.simulation_builder import SimulationBuilder

    original_set_input = CoreSimulation.set_input
    if not getattr(original_set_input, "_social_security_compatibility", False):

        @wraps(original_set_input)
        def set_input(simulation, variable_name, period, value):
            track_public_write = (
                variable_name in SOCIAL_SECURITY_COMPONENTS
                and getattr(
                    simulation.tax_benefit_system,
                    "_social_security_input_compatibility",
                    False,
                )
                and hasattr(simulation, "input_variables")
                and not _initial_social_security_ingress.get()
            )
            if not track_public_write:
                return original_set_input(simulation, variable_name, period, value)

            holder = simulation.get_holder(variable_name)
            branch = simulation.branch_name
            before = {
                supplied_period: holder._stored_sequence_number(supplied_period, branch)
                for supplied_period in simulation._get_set_input_periods(variable_name)
            }
            result = original_set_input(simulation, variable_name, period, value)
            reported_name = f"{variable_name}_reported"
            reported_periods = set(simulation._get_set_input_periods(reported_name))
            # Period helpers can store a different period from the one passed
            # in: a monthly input to a yearly variable stores a rolling year.
            # Inspect actual stores rather than guessing those period aliases.
            for supplied_period in simulation._get_set_input_periods(variable_name):
                if (
                    holder._stored_sequence_number(supplied_period, branch)
                    == before.get(supplied_period)
                    or supplied_period in reported_periods
                ):
                    continue
                supplied_value = simulation._get_recorded_input_array(
                    variable_name, supplied_period
                )
                if supplied_value is not None:
                    original_set_input(
                        simulation,
                        reported_name,
                        supplied_period,
                        supplied_value.copy(),
                    )

            # Core clones share this legacy list. Replace it privately so a
            # later override is extracted without changing the source clone.
            simulation.input_variables = list(
                dict.fromkeys(
                    [*simulation.input_variables, variable_name, reported_name]
                )
            )
            return result

        set_input._social_security_compatibility = True
        CoreSimulation.set_input = set_input

    def wrap_builder(original_build):
        @wraps(original_build)
        def build(builder, tax_benefit_system, input_dict, simulation=None):
            if not getattr(
                tax_benefit_system, "_social_security_input_compatibility", False
            ):
                return original_build(
                    builder, tax_benefit_system, input_dict, simulation
                )
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
            migrate_social_security_inputs(result)
            return result

        build._social_security_compatibility = True
        return build

    for method_name in ("build_from_entities", "build_from_variables"):
        original_build = getattr(SimulationBuilder, method_name)
        if not getattr(original_build, "_social_security_compatibility", False):
            setattr(SimulationBuilder, method_name, wrap_builder(original_build))


def migrate_social_security_inputs(simulation, *, include_baseline=True):
    """Move legacy component inputs, period by period, into pure sources.

    A reported input in the same visible period makes the public input a
    deliberate final override. Inputs in other periods do not affect that
    choice. Recorded-input helpers exclude formula caches and honor visible
    branch precedence.
    """
    visible_branches = simulation._get_visible_branch_names()
    migrated = set()
    for public_name in SOCIAL_SECURITY_COMPONENTS:
        reported_name = f"{public_name}_reported"
        reported_periods = set(simulation._get_set_input_periods(reported_name))
        holder = simulation.get_holder(public_name)
        # Snapshot before deleting: deleting a multi-year period also deletes
        # contained supplied periods, including a shorter legacy source whose
        # lexical sort order happens to place it after the longer period.
        sources = {}
        for period in simulation._get_set_input_periods(public_name):
            if period not in reported_periods:
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
                or period not in reported_periods
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

    This is the complete-history alternative to Core's legacy one-period
    ``extract_person`` API. Export the desired small simulation or household;
    this helper deliberately does not materialize a population dataset.
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
    simulation = Simulation(situation=payload["sources"], **simulation_kwargs)
    for name, periods in payload["overrides"].items():
        for period, values in periods.items():
            simulation.set_input(name, period, values)
    simulation.input_variables = list(
        dict.fromkeys([*simulation.input_variables, *payload["overrides"]])
    )
    return simulation
