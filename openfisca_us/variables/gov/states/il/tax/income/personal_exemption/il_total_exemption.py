from openfisca_us.model_api import *


class il_total_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL total exemption allowance"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        total_amount = (
            tax_unit("il_personal_exemption", period)
            + tax_unit("il_aged_blind_exemption", period)
            + tax_unit("il_dependent_exemption", period)
        )

        return where(
            tax_unit("il_is_exemption_eligible", period), total_amount, 0
        )
