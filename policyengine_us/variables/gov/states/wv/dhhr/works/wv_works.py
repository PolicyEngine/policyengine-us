from policyengine_us.model_api import *


class wv_works(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia WV Works benefit"
    unit = USD
    definition_period = MONTH
    reference = "https://bfa.wv.gov/media/2766/download?inline#page=589"
    defined_for = "wv_works_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.works
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.max_household_size)
        # Step 8: Determine the maximum WV WORKS benefit amount for the AG size
        payment_standard = p.payment_standard.amount[capped_size]
        # Step 9: Eligibility check (handled by defined_for = "wv_works_eligible")
        # Step 10: Subtract countable income from payment standard
        countable_income = spm_unit("wv_works_countable_income", period)
        benefit = max_(payment_standard - countable_income, 0)
        return min_(benefit, payment_standard)
