from openfisca_us.model_api import *


class high_efficiency_electric_home_rebate(Variable):
    value_type = float
    entity = Household
    label = "High efficiency electric home rebate"
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        p = parameters(period).gov.doe.high_efficiency_electric_home_rebate
        # Sum (capped) per-expenditure rebates.
        uncapped = add(household, period, ["capped_" + i + "_rebate" for i in p.elements])
        return min_(uncapped, p.cap.total)
