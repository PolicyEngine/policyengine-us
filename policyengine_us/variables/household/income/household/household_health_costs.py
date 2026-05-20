from policyengine_us.model_api import *


class household_health_costs(Variable):
    value_type = float
    entity = Household
    label = "Household health costs"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Household out-of-pocket health costs such as CHIP premiums. Included "
        "in net income only when health benefits are counted as income, so "
        "that the costs and benefits are accounted for symmetrically."
    )

    def formula(household, period, parameters):
        p = parameters(period)
        if p.gov.simulation.include_health_benefits_in_net_income:
            return add(household, period, p.gov.household.household_health_costs)
        return 0
