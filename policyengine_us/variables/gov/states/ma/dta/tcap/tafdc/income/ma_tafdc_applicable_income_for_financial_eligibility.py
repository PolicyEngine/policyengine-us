from policyengine_us.model_api import *


class ma_tafdc_applicable_income_for_financial_eligibility(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Applicable income for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) financial eligibility check"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-260"
    defined_for = StateCode.MA

    # 106 CMR 704.260 counts income net of "the disregarded income as provided
    # in 106 CMR 704.270, 704.275, 704.280 and 704.281".
    # ma_tafdc_partially_disregarded_earned_income carries all three earned
    # income steps: the 704.270 work-related expense deduction, the 704.281(B)
    # 50% disregard and the 704.275 dependent care deduction.
    # 704.281(A)'s six-month 100% disregard is deliberately left out: it runs
    # "for purposes of the grant calculation" only, for clients who have
    # already been found eligible, so it belongs to
    # ma_tafdc_applicable_income_grant_amount rather than to this test.
    adds = [
        "ma_tafdc_partially_disregarded_earned_income",
        "ma_tafdc_countable_unearned_income",
    ]
