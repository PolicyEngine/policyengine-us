from openfisca_us.model_api import *


class capped_electric_load_service_center_upgrade_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped electric load service center upgrade rebate"
    documentation = "Before total high efficiency electric home rebate cap"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        percent_covered = tax_unit(
            "high_efficiency_electric_home_rebate_percent_covered", period
        )
        expenditures = tax_unit(
            "electric_load_service_center_upgrade_expenditures", period
        )
        cap = parameters(
            period
        ).gov.doe.high_efficiency_electric_home_rebate.cap.electric_load_service_center_upgrade
        return min_(expenditures * percent_covered, cap)
