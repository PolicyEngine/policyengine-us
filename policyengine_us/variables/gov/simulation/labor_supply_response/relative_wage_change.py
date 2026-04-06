from policyengine_us.model_api import *
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    calculate_relative_wage_change,
    get_behavioral_response_measurements,
)


class relative_wage_change(Variable):
    value_type = float
    entity = Person
    label = "relative wage change"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_behavioral_response"

    def formula(person, period, parameters):  # pragma: no cover
        p = parameters(period).gov.simulation.labor_supply_responses
        measurements = get_behavioral_response_measurements(person, period)
        return calculate_relative_wage_change(measurements, p.bounds)
