from policyengine_us.model_api import *


class medicaid_cost_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Medicaid cost if enrolled"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        spending = parameters(period).calibration.gov.hhs.medicaid.totals.spending
        cost_index = person("medicaid_slcsp_cost_index_filled", period)
        denominator = person("medicaid_slcsp_state_denominator", period)

        return np.divide(
            spending[state_code] * cost_index,
            denominator,
            out=np.zeros_like(denominator),
            where=denominator > 0,
        )
