from policyengine_us.model_api import *


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
        self_employment_income_ind = person(
            "taxable_self_employment_income", period
        )
        self_employment_income = spm_unit.sum(self_employment_income_ind)

        # Get the policy parameters.

        return select(
            # First arg: self employed or not
            [self_employment_income > 0, earned_income > 0],
            # Second arg: multiply by the percent deduction (0.2, 0.5)
            [self_employment_income * p.self_employed, earned_income * p.new],
            # Third arg: default value to return if none of the conditions are True
            default=0,
        )
        # Return if initially eligible
