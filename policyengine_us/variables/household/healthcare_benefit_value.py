from policyengine_us.model_api import *


class healthcare_benefit_value(Variable):
    value_type = float
    label = "cash equivalent of health coverage"
    entity = Household
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        # sum over all household members’ benefit variables
        return add(household, period, ["medicaid_per_capita_cost", "per_capita_chip", "aca_ptc"])
