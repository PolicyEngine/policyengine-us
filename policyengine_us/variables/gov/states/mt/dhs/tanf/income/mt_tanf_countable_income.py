from policyengine_us.model_api import *


class mt_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://dphhs.mt.gov/assets/hcsd/tanfmanual/tanf602-1jan012018.pdf#page=1"
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        countable_earned = spm_unit("mt_tanf_countable_earned_income", period)
        dependent_care_deduction = spm_unit(
            "mt_tanf_dependent_care_deduction", period
        )
        earned_after_deductions = max_(
            countable_earned - dependent_care_deduction, 0
        )
        countable_unearned = spm_unit("mt_tanf_gross_unearned_income", period)
        return earned_after_deductions + countable_unearned
