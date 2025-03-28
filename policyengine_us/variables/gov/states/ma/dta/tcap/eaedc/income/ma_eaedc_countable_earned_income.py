from policyengine_us.model_api import *


class ma_eaedc_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500"  # (B) step 2

    def formula(spm_unit, period, parameters):
        total_earned_income_after_disregard = add(
            spm_unit, period, ["ma_eaedc_earned_income_after_disregard_person"]
        )
        # dependent care deduction
        dependent_care_deduction = add(
            spm_unit, period, ["ma_eaedc_dependent_care_deduction_person"]
        )

        return max_(
            total_earned_income_after_disregard - dependent_care_deduction, 0
        )
