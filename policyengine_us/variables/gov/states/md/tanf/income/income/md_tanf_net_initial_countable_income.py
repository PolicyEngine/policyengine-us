from policyengine_us.model_api import *


class md_tanf_net_initial_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF net initial countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0902%20TCA%20Earned%20Income%20rev%2011.22.doc"

    def formula(spm_unit, period, parameters):
        # Get gross income for the SPM unit.
        gross_earned_income = spm_unit(
            "md_tanf_countable_gross_earned_income", period
        )
        gross_unearned_income = spm_unit(
            "md_tanf_countable_gross_unearned_income", period
        )
        # Get initial deductions for the SPM unit.
        initial_deductions = spm_unit(
            "md_tanf_initial_earnings_deduction", period
        )
        # Get childcare deductions for the SPM unit.
        childcare_deduction = spm_unit("md_tanf_childcare_deduction", period)
        # Apply deductions to earned income only, then add unearned
        countable_earned = max_(
            gross_earned_income - initial_deductions - childcare_deduction,
            0,
        )
        return countable_earned + gross_unearned_income
