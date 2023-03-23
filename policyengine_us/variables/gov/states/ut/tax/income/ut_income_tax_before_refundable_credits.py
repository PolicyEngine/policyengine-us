from policyengine_us.model_api import *


class ut_income_tax_before_refundable_credits(Variable):
    """
    Line 32 of Utah 2022 Individual Income Tax return form TC-40.
    """

    value_type = float
    entity = TaxUnit
    label = "UT income tax before refundable credits"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income_tax_after_credits = tax_unit(
            "ut_income_tax_after_credits", period
        )
        apportionable_nonrefundable_credits = tax_unit(
            "ut_apportionable_nonrefundable_credits", period
        )
        nonapportionable_nonrefundable_credits = tax_unit(
            "ut_nonapportionable_nonrefundable_credits", period
        )
        income_tax_before_additions = max_(
            income_tax_after_credits
            - apportionable_nonrefundable_credits
            - nonapportionable_nonrefundable_credits,
            0,
        )
        recapture_low_inc_housing_credit = tax_unit(
            "ut_recapture_low_inc_housing_credit", period
        )
        return income_tax_before_additions + recapture_low_inc_housing_credit
