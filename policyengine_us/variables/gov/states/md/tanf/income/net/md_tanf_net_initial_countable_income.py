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
        gross_earned_income = spm_unit("md_tanf_gross_earned_income", period)
        gross_unearned_income = spm_unit("md_tanf_gross_unearned_income", period)
        # Get initial deductions for the SPM unit.
        initial_deductions = spm_unit("md_tanf_initial_deductions", period)
        # Get alimony deductions for the SPM unit.
        p1 = parameters(period).household.income.person.misc
        alimony_deduction = add(spm_unit, period, p1.alimony_income)
        # Get child support deductions for the SPM unit.
        p2 = parameters(period).household.expense.child_support
        child_support_deduction = add(spm_unit, period, p2.child_support_received)
        # Get childcare deductions for the SPM unit.
        childcare_deduction = spm_unit("md_tanf_childcare_deduction", period)

        return gross_earned_income + gross_unearned_income - initial_deductions - alimony_deduction - child_support_deduction - childcare_deduction
