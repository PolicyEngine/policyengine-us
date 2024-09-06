from policyengine_us.model_api import *


class nj_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        main_income_tax = tax_unit("nj_main_income_tax", period)
        non_refundable_credits = tax_unit("nj_non_refundable_credits", period)

        return max_(main_income_tax - non_refundable_credits, 0)
