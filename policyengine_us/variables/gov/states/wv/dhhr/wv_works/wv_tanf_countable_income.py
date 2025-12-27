from policyengine_us.model_api import *


class wv_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia WV Works countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dhhr.wv.gov/bcf/Services/familyassistance/Pages/WV-WORKS.aspx"
    )
    defined_for = StateCode.WV

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.wv_works.income
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        # Apply 40% disregard to earned income only
        countable_earned = gross_earned * (1 - p.earned_income_disregard.rate)
        return max_(countable_earned, 0) + gross_unearned
