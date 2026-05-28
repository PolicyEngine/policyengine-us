from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.state_aggregate import (
    sum_by_state,
)


class medicaid_slcsp_state_denominator(Variable):
    value_type = float
    entity = Person
    label = "Medicaid SLCSP state allocation denominator"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        state_code = person.household("state_code", period)
        cost_index = person("medicaid_slcsp_cost_index_filled", period)
        weight = person("person_weight", period)
        enrolled = person("medicaid_enrolled", period)
        state_denominator = sum_by_state(weight * cost_index * enrolled, state)

        if person.simulation.is_over_dataset:
            return state_denominator

        p = parameters(period).calibration.gov.hhs.medicaid.totals
        return p.enrollment[state_code] * person(
            "medicaid_slcsp_state_average_cost_index", period
        )
