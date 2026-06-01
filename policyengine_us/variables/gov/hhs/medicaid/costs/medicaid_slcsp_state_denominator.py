from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.state_aggregate_helpers import (
    sum_by_state,
)


class medicaid_slcsp_state_denominator(Variable):
    value_type = float
    entity = Person
    label = "Medicaid SLCSP state allocation denominator"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        simulation = person.simulation
        if simulation.baseline is not None and simulation.branch_name != "baseline":
            baseline_person = simulation.baseline.populations["person"]
            return baseline_person("medicaid_slcsp_state_denominator", period)

        state_code = person.household("state_code", period)
        if simulation.is_over_dataset:
            state = person.household("state_code_str", period)
            cost_index = person("medicaid_slcsp_cost_index_filled", period)
            weight = person("person_weight", period)
            enrolled = person("medicaid_enrolled", period)
            return sum_by_state(weight * cost_index * enrolled, state)

        # Single household: no population to sum, so estimate the denominator
        # as state enrollment times the state-average index.
        p = parameters(period).calibration.gov.hhs.medicaid.totals
        return p.enrollment[state_code] * person(
            "medicaid_slcsp_state_average_cost_index", period
        )
