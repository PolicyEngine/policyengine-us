from openfisca_us.model_api import *


class capped_electric_heat_pump_clothes_dryer_rebate(Variable):
    value_type = float
    entity = Household
    label = "Capped electric heat pump clothes dryer rebate"
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
            ["electric_heat_pump_clothes_dryer_expenditures"],
        )
        cap = parameters(
            period
        ).gov.doe.high_efficiency_electric_home_rebate.cap.electric_heat_pump_clothes_dryer
        return min_(expenditures * percent_covered, cap)
