from openfisca_us.model_api import *


class capped_insulation_air_sealing_and_ventilation_rebate(Variable):
    value_type = float
    entity = Household
    label = "Capped insulation air sealing and ventilation rebate"
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
            ["insulation_air_sealing_and_ventilation_expenditures"],
        )
        cap = parameters(
            period
        ).gov.doe.high_efficiency_electric_home_rebate.cap.insulation_air_sealing_and_ventilation
        return min_(expenditures * percent_covered, cap)
