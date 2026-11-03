"""Read legacy annual inputs without averaging calculated monthly budgets."""

from policyengine_us.model_api import has_input_for_period


def annual_input(person, period, name):
    """Return a supplied annual input, or None to calculate the monthly budget.

    A calculated annual aggregate must never replace a month's own budget.
    Recording the input-presence dependency also lets Core invalidate cached
    monthly budgets when a branch supplies its first annual override later.
    """
    simulation = person.simulation
    holder = simulation.get_holder(name)
    # Core 3.33+ records dependencies by store order. Older supported Core
    # versions rely on callers clearing branch caches with get_override_branch.
    if hasattr(holder, "_record_store"):
        from policyengine_core.data_storage.store_history import next_sequence_number

        holder._record_store(period.this_year, next_sequence_number())

    abolished = simulation.tax_benefit_system.parameters(
        period.this_year
    ).gov.abolitions[name]
    if (
        holder.variable.is_neutralized
        or abolished
        or has_input_for_period(simulation, name, period.this_year)
    ):
        return person(name, period.this_year)
    return None
