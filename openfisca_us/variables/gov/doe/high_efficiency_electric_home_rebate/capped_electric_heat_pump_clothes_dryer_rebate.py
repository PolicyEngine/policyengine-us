from openfisca_us.model_api import *


class capped_electric_heat_pump_clothes_dryer_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped electric heat pump clothes dryer rebate"
    documentation = "Before total high efficiency electric home rebate cap"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        percent_covered = tax_unit(
            "high_efficiency_electric_home_rebate_percent_covered", period
        )
        expenditures = tax_unit(
            "electric_heat_pump_clothes_dryer_expenditures", period
        )
        cap = parameters(
            period
        ).gov.doe.high_efficiency_electric_home_rebate.cap.electric_heat_pump_clothes_dryer
        return min_(expenditures * percent_covered, cap)
