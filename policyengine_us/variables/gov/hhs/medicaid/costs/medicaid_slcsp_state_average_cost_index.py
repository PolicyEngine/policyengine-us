from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.state_aggregate_helpers import (
    sum_by_state,
)


class medicaid_slcsp_state_average_cost_index(Variable):
    value_type = float
    entity = Person
    label = "Average Medicaid SLCSP cost index in each state"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        if person.simulation.is_over_dataset:
            group = person.household("state_code_str", period)
        else:
            group = person.simulation.populations["household"].members_entity_id
        cost_index = person("medicaid_slcsp_cost_index", period)
        weight = person("person_weight", period)
        positive_index = cost_index > 0
        group_weight = sum_by_state(weight * positive_index, group)
        group_cost_index = sum_by_state(weight * cost_index * positive_index, group)

        # Group dataset people by state and situation people by household.
        # Retain the fallback of 1 when the group has no positive-index weight.
        return np.divide(
            group_cost_index,
            group_weight,
            out=np.ones_like(cost_index),
            where=group_weight > 0,
        )
