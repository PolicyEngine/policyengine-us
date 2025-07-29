from policyengine_us.model_api import *


class household_health_benefits(Variable):
    value_type = float
    entity = Household
    label = "Household health benefits"
    unit = USD
    definition_period = YEAR

    def formula(household, period, parameters):
        p = parameters(period)
        if p.gov.simulation.include_health_benefits_in_net_income:
            return add(
                household, period, p.gov.household.household_health_benefits
            )
        else:
            return 0
