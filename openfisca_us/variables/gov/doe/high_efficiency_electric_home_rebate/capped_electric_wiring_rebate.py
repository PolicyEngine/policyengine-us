from openfisca_us.model_api import *


class capped_electric_wiring_rebate(Variable):
    value_type = float
    entity = Household
    label = "Capped electric wiring rebate"
    documentation = "Before total high efficiency electric home rebate cap"
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        percent_covered = household(
            "high_efficiency_electric_home_rebate_percent_covered", period
        )
        expenditures = add(household, period, ["electric_wiring_expenditures"])
        cap = parameters(
            period
        ).gov.doe.high_efficiency_electric_home_rebate.cap.electric_wiring
        return min_(expenditures * percent_covered, cap)
