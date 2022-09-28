from openfisca_us.model_api import *


class mo_adjusted_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "",
        "",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        subtractions = tax_unit(
            "mo_qualified_health_insurance_premiums", period
        )
        return max_(agi - subtractions, 0)
