from policyengine_us.model_api import *
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    calculate_income_lsr_effect,
    calculate_substitution_lsr_effect,
    get_behavioral_response_measurements,
)


class labor_supply_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "earnings-related labor supply change"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.simulation.labor_supply_responses
        simulation = person.simulation
        if simulation.baseline is None:
            return 0  # No reform, no impact
        if p.elasticities.income == 0 and p.elasticities.substitution.all == 0:
            return 0

        # Guard against re-entry (prevents recursion when branches calculate variables)
        if (  # pragma: no cover
            hasattr(simulation, "_lsr_calculating") and simulation._lsr_calculating
        ):
            return 0

        # Mark that we're calculating LSR
        simulation._lsr_calculating = True  # pragma: no cover

        try:  # pragma: no cover
            measurements = get_behavioral_response_measurements(person, period)
            return calculate_income_lsr_effect(
                person, period, parameters, measurements
            ) + calculate_substitution_lsr_effect(
                person, period, parameters, measurements
            )

        finally:
            # Clear the re-entry guard
            simulation._lsr_calculating = False
