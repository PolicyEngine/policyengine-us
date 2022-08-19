from openfisca_us.model_api import *


class md_income_tax_after_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax after non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        tax_before_credits = tax_unit("md_income_tax_before_credits", period)
        non_refundable_credits = tax_unit("md_non_refundable_credits", period)
        return max_(0, tax_before_credits - non_refundable_credits)
