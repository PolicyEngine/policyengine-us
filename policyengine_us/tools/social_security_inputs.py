"""Compatibility ingress and complete, source-safe simulation snapshots.

Constructor migration is intentionally separate from ``set_input``: a later
write to a public benefit is an output override, including an explicit zero.
"""

import json

from policyengine_core.simulations.simulation import NpEncoder

from policyengine_us.tools.period_branch import delete_input_values


SOCIAL_SECURITY_COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)


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
        for period in simulation._get_set_input_periods(public_name):
            if period in reported_periods:
                continue
            value = simulation._get_recorded_input_array(public_name, period)
            if value is None:
                continue
            simulation.set_input(reported_name, period, value.copy())
            for branch_name in visible_branches:
                delete_input_values(holder, period, branch_name)
            migrated.add(public_name)

    # Core's legacy extraction reads this runtime list, which was assembled
    # before migration. Retain public names only where actual overrides remain.
    runtime_inputs = []
    for name in simulation.input_variables:
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
