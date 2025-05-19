from policyengine_us.model_api import *

class healthcare_benefit_value(Variable):
    value_type = float
    label = "cash equivalent of health coverage"
    entity = Household       
    definition_period = YEAR
    unit = USD

    def formula(hh, period, parameters):
        # sum over all household members’ benefit variables
        return add(hh, period, ["medicaid_benefit_value",
                                "chip_benefit_value",
                                "premium_tax_credit"])
