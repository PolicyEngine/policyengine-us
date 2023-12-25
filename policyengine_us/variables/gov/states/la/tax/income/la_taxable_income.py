from policyengine_us.model_api import *


class la_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana taxable income"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return max_(
            tax_unit("la_agi", period)
            - tax_unit("la_itemized_deductions", period)
            - tax_unit("la_exemptions", period),
            0,
        )
