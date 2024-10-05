from policyengine_us.model_api import *


class capped_electric_wiring_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped electric wiring rebate"
    documentation = "Before total high efficiency electric home rebate cap"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        percent_covered = tax_unit(
            "high_efficiency_electric_home_rebate_percent_covered", period
        )
        expenditures = tax_unit("electric_wiring_expenditures", period)
        cap = parameters(
            period
        ).gov.doe.high_efficiency_electric_home_rebate.cap.electric_wiring
        return min_(expenditures * percent_covered, cap)
