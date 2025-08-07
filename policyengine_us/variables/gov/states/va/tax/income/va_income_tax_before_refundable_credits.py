from policyengine_us.model_api import *


class va_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        tax_before_non_refundable_credits = tax_unit(
            "va_income_tax_before_non_refundable_credits", period
        )
        non_refundable_credits = tax_unit("va_non_refundable_credits", period)
        spouse_tax_adjustment = tax_unit("va_spouse_tax_adjustment", period)
        return max_(
            tax_before_non_refundable_credits
            - non_refundable_credits
            - spouse_tax_adjustment,
            0,
        )
