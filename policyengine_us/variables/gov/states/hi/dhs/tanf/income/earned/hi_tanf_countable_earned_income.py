from policyengine_us.model_api import *


class hi_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=19",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        # Sum person-level countable earned income
        earned = add(
            spm_unit, period, ["hi_tanf_countable_earned_income_person"]
        )

        # Subtract dependent care deduction (work expense)
        dependent_care = spm_unit("hi_tanf_dependent_care_deduction", period)

        # Floor at 0 - dependent care can't reduce earned below zero
        return max_(earned - dependent_care, 0)
