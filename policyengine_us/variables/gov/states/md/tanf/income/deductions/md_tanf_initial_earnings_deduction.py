from policyengine_us.model_api import *


class md_tanf_initial_earnings_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA initial earnings deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.tanf.income.deductions.earned
        earned_income = spm_unit(
            "md_tanf_countable_gross_earned_income", period
        )
        # Determine if the SPM unit has any self-employment income.
        self_employment_income = spm_unit(
            "md_tanf_self_employment_income", period
        )
        non_self_employment_income = max_(
            earned_income - self_employment_income, 0
        )

        return (self_employment_income * p.self_employed) + (
            non_self_employment_income * p.new
        )
