from policyengine_us.model_api import *


class md_tanf_net_initial_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF net initial countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        # Get gross income for the SPM unit.
        gross_earned_income = spm_unit(
            "md_tanf_countable_gross_earned_income", period
        )
        gross_unearned_income = spm_unit(
            "md_tanf_countable_gross_unearned_income", period
        )
        # Get countinuous deductions for the SPM unit.
        initial_deductions = spm_unit(
            "md_tanf_initial_earnings_deduction", period
        )
        # Get alimony deductions for the SPM unit.
        person = spm_unit.members
        alimony_deduction_ind = person("alimony_income", period)
        alimony_deduction = spm_unit.sum(alimony_deduction_ind)
        # Get child support deductions for the SPM unit.
        child_support_deduction_ind = person("child_support_received", period)
        child_support_deduction = spm_unit.sum(child_support_deduction_ind)
        # Get childcare deductions for the SPM unit.
        childcare_deduction = spm_unit("md_tanf_childcare_deduction", period)

        return (
            gross_earned_income
            + gross_unearned_income
            - initial_deductions
            - alimony_deduction
            - child_support_deduction
            - childcare_deduction
        )
