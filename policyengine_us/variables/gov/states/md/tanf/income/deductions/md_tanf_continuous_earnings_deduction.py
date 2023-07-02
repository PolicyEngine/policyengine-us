from policyengine_us.model_api import *

# href: https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0904%20Deductions%20and%20Expenses%20rev%2011.22.1.doc
#       page 1


class md_tanf_continuous_earnings_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF continuous earnings deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.md.tanf.income.deductions.earnings_exclusion
        earned_income = spm_unit(
            "md_tanf_countable_gross_earned_income", period
        )
        self_employment_income = spm_unit(
            "md_tanf_self_employment_income", period
        )
        non_self_employment_income = max_(
            earned_income - self_employment_income, 0
        )
        return (self_employment_income * p.self_employed) + (
            non_self_employment_income * p.not_self_employed
        )
