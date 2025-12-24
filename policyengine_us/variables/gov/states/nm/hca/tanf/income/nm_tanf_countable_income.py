from policyengine_us.model_api import *


class nm_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # Per 8.102.520 NMAC, calculate countable income:
        # Countable = Countable Earned + Countable Unearned - Child Care
        countable_earned = spm_unit("nm_tanf_countable_earned_income", period)
        countable_unearned = spm_unit(
            "nm_tanf_countable_unearned_income", period
        )
        child_care_deduction = spm_unit("nm_tanf_child_care_deduction", period)
        return max_(
            countable_earned + countable_unearned - child_care_deduction, 0
        )
