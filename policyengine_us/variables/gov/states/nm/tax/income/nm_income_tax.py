from policyengine_us.model_api import *


class nm_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        before_non_refundable_credits = tax_unit("nm_income_tax_before_non_refundable_credits", period)
        non_refundable_credits = tax_unit("nm_non_refundable_credit", period)
        refundable_credits = tax_unit("nm_refundable_credits", period)
        capped_non_refunable_credits = max_(before_non_refundable_credits - non_refundable_credits, 0)
        return capped_non_refunable_credits - refundable_credits
