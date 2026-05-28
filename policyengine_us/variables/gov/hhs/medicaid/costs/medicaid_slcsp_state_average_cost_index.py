from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.state_aggregate import (
    sum_by_state,
)


class medicaid_slcsp_state_average_cost_index(Variable):
    value_type = float
    entity = Person
    label = "Average Medicaid SLCSP cost index in each state"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        cost_index = person("medicaid_slcsp_cost_index", period)
        weight = person("person_weight", period)
        positive_index = cost_index > 0
        state_weight = sum_by_state(weight * positive_index, state)
        state_cost_index = sum_by_state(weight * cost_index * positive_index, state)

        return np.divide(
            state_cost_index,
            state_weight,
            out=np.ones_like(cost_index),
            where=state_weight > 0,
        )
