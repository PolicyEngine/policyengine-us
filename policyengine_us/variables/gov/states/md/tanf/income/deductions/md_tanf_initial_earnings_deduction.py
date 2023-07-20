from policyengine_us.model_api import *

# reference: https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0902%20TCA%20Earned%20Income%20rev%2011.22.doc


class md_tanf_initial_earnings_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF initial earnings deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # Get earned income for the SPM unit.
        p = parameters(
            period
        ).gov.states.md.tanf.income.deductions.earnings_exclusion
        earned_income = spm_unit(
            "md_tanf_countable_gross_earned_income", period
        )
        # Determine if the SPM unit has any self-employment income.
        self_employment_income = spm_unit(
            "md_tanf_self_employment_income", period
        )
        non_self_employment_income = earned_income - self_employment_income
        # Get the policy parameters.

        return (self_employment_income * p.self_employed) + (
            non_self_employment_income * p.new
        )
