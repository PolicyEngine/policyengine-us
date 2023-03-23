from policyengine_us.model_api import *


class ut_income_tax_after_credits(Variable):
    """
    Line 22 of Utah 2022 Individual Income Tax return form TC-40.
    """

    value_type = float
    entity = TaxUnit
    label = "UT income tax after standard nonrefundable credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit(
            "ut_income_tax_before_credits", period
        )
        standard_non_refundable_credits = tax_unit(
            "ut_taxpayer_credit", period
        )
        return max_(
            income_tax_before_credits - standard_non_refundable_credits, 0
        )
