from policyengine_us.model_api import *

# reference: https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0902%20TCA%20Earned%20Income%20rev%2011.22.doc


class md_tanf_net_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF net countable income"
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
        continuous_deductions = spm_unit(
            "md_tanf_continuous_earnings_deduction", period
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
            - continuous_deductions
            - alimony_deduction
            - child_support_deduction
            - childcare_deduction
        )
