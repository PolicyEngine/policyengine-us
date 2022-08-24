from openfisca_us.model_api import *


class capped_heat_pump_rebate(Variable):
    value_type = float
    entity = Household
    label = "Capped heat pump rebate"
    documentation = "Before total high efficiency electric home rebate cap"
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        percent_covered = household(
            "high_efficiency_electric_home_rebate_percent_covered", period
        )
        expenditures = add(household, period, ["heat_pump_expenditures"])
        cap = parameters(
            period
        ).gov.doe.high_efficiency_electric_home_rebate.cap.heat_pump
        return min_(expenditures * percent_covered, cap)
