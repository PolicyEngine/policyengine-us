from openfisca_us.model_api import *


class capped_electric_stove_cooktop_range_or_oven_rebate(Variable):
    value_type = float
    entity = Household
    label = "Capped electric stove cooktop range or oven rebate"
    documentation = "Before total high efficiency electric home rebate cap"
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        percent_covered = household(
            "high_efficiency_electric_home_rebate_percent_covered", period
        )
        expenditures = add(
            household,
            period,
            ["electric_stove_cooktop_range_or_oven_expenditures"],
        )
        cap = parameters(
            period
        ).gov.doe.high_efficiency_electric_home_rebate.cap.electric_stove_cooktop_range_or_oven
        return min_(expenditures * percent_covered, cap)
