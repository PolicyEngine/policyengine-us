"""Read legacy annual inputs without averaging calculated monthly budgets."""

from policyengine_core.data_storage.store_history import next_sequence_number

from policyengine_us.model_api import has_input_for_period


def annual_input(person, period, name):
    """Return a supplied annual input, or None to calculate the monthly budget.

    A calculated annual aggregate must never replace a month's own budget.
    Recording the input-presence dependency also lets Core invalidate cached
    monthly budgets when a branch supplies its first annual override later.
    """
    simulation = person.simulation
    holder = simulation.get_holder(name)
    # Core records dependencies by store order. It has no public method for
    # this record, so the adapter calls the holder's private one.
    holder._record_store(period.this_year, next_sequence_number())

    # Monthly readers retain dated abolition switches on the annual name.
    if simulation.tax_benefit_system.parameters(period).gov.abolitions[name]:
        return 0

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
