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

        substitution_elasticities = p.elasticities.substitution
        by_position = getattr(substitution_elasticities, "by_position_and_decile", None)
        primary_elasticities = (
            getattr(by_position, "primary", None) if by_position else None
        )
        no_income_response = p.elasticities.income == 0
        no_substitution_response = (
            substitution_elasticities.all == 0
            and getattr(by_position, "secondary", 0) == 0
            and all(
                getattr(primary_elasticities, str(decile), 0) == 0
                for decile in range(1, 11)
            )
        )
        if no_income_response and no_substitution_response:
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
