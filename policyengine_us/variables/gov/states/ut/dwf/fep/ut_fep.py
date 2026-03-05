from policyengine_us.model_api import *


class ut_fep(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah Family Employment Program benefit"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-239"
    defined_for = "ut_fep_eligible"

    def formula(spm_unit, period, parameters):
        # Per R986-200-239(6): Benefit = payment standard - countable income
        payment_standard = spm_unit("ut_fep_payment_standard", period)
        countable_income = spm_unit("ut_fep_countable_income", period)
        benefit = max_(payment_standard - countable_income, 0)
        return min_(benefit, payment_standard)
