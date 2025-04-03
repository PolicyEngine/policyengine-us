from policyengine_us.model_api import *


class dc_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC Temporary Assistance for Needy Families (TANF) countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11"
    )

    def formula(spm_unit, period, parameters):
        total_earned_income_after_disregard = add(
            spm_unit, period, ["dc_tanf_earned_income_after_disregard_person"]
        )

        child_care_deduction = spm_unit("dc_tanf_childcare_deduction", period)

        return max_(
            total_earned_income_after_disregard - child_care_deduction, 0
        )
