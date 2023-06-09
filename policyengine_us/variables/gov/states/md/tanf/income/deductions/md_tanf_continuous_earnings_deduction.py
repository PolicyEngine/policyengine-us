from policyengine_us.model_api import *


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

        return select(
            # First arg: self employed or not
            [self_employment_income > 0, earned_income > 0],
            # Second arg: multiply by the percent deduction (0.4, 0.5)
            [
                self_employment_income * p.self_employed,
                earned_income * p.not_self_employed,
            ],
            # Third arg: default value to return if none of the conditions are True
            default=0,
        )
