from policyengine_us.model_api import *


class ut_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah Family Employment Program benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = "ut_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Per R986-200-246: Benefit = payment standard - countable income
        payment_standard = spm_unit("ut_tanf_payment_standard", period)
        countable_income = spm_unit("ut_tanf_countable_income", period)
        return max_(payment_standard - countable_income, 0)
