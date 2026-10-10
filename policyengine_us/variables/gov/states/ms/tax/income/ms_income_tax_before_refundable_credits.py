from policyengine_us.model_api import *


class ms_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    # Form 80-105 line 17 (total income tax due) less the credits on lines
    # 18 and 19, which may not exceed it.
    reference = "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=8"
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        tax_before_credits = tax_unit("ms_income_tax_before_credits_unit", period)
        non_refundable_credits = tax_unit("ms_non_refundable_credits", period)
        return max_(tax_before_credits - non_refundable_credits, 0)
