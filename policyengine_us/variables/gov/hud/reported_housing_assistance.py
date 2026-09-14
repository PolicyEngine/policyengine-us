from policyengine_us.model_api import *


class reported_housing_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing assistance received"
    unit = USD
    definition_period = YEAR
    documentation = """
    Housing assistance for a unit that reports receiving it, and zero otherwise.

    PG&E Form 01-9077, the CARE/FERA application, counts "housing and military
    subsidies" among the revenues making up total gross annual household
    income. The form asks an applicant what the household receives, so the
    subsidy it counts is one the household actually holds.

    `housing_assistance` is not that: `is_eligible_for_housing_assistance` is
    `receives_housing_assistance | (is_renter & is_income_eligible)` and
    `takes_up_housing_assistance_if_eligible` defaults to true, so any
    income-eligible renter who supplies rent is modelled as holding a voucher.
    Gating on `receives_housing_assistance` - an input, defaulting to false -
    counts the reported receipt and leaves imputed take-up out of the income
    definitions that ask for it.
    """
    reference = "https://www.pge.com/assets/pge/localized/en/docs/account/billing-and-assistance/care-fera-application.pdf"

    def formula(spm_unit, period, parameters):
        receives = spm_unit("receives_housing_assistance", period)
        return where(receives, spm_unit("housing_assistance", period), 0)
