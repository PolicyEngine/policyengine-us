from policyengine_us.model_api import *


class ut_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = (
        "https://tax.utah.gov/forms/current/tc-40.pdf#page=1"  # line 22
    )

    def formula(tax_unit, period, parameters):
        taxpayer_credit = tax_unit("ut_taxpayer_credit", period)
        ut_income_tax_before_credits = tax_unit(
            "ut_income_tax_before_credits", period
        )
        is_tax_liable = ~tax_unit("ut_income_tax_exempt", period)
        net_income_tax_before_credits = max_(
            ut_income_tax_before_credits - taxpayer_credit, 0
        )
        return is_tax_liable * net_income_tax_before_credits
