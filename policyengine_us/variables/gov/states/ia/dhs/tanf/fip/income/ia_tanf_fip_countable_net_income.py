from policyengine_us.model_api import *


class ia_tanf_fip_countable_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP countable net income for benefit calculation"
    unit = USD
    definition_period = MONTH
    reference = "Iowa HHS FIP Budgeting Manual Chapter 4-F"
    documentation = "https://hhs.iowa.gov/media/3972/download?inline"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Start with gross earned income
        gross_earned = spm_unit("ia_tanf_fip_gross_earned_income", period)

        # Apply 20% earned income deduction
        earned_deduction = spm_unit(
            "ia_tanf_fip_earned_income_deduction", period
        )

        # Apply 50% work incentive deduction (only if passed Standard of Need test)
        work_incentive = spm_unit(
            "ia_tanf_fip_work_incentive_deduction", period
        )

        # Add unearned income
        unearned = spm_unit("ia_tanf_fip_gross_unearned_income", period)

        # Calculate countable net income
        countable_net = (
            gross_earned - earned_deduction - work_incentive + unearned
        )

        return max_(countable_net, 0)
