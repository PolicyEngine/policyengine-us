from policyengine_us.model_api import *


class md_tanf_gross_earned_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF earned income deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        # set up spm_unit
        person = spm_unit.members
        # Get TANF enrollment status.
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        # Get earned income for the SPM unit.
        earned_income = spm_unit(
            "md_tanf_countable_gross_earned_income", period
        )

        p = parameters(
            period
        ).gov.states.md.tanf.income.deductions.earnings_exclusion
        # Determine if the SPM unit has any self-employment income.
        self_employment_income_ind = person(
            "taxable_self_employment_income", period
        )
        self_employment_income = spm_unit.sum(self_employment_income_ind)

        percent = select(
            # First arg: list of conditions
            [~is_tanf_enrolled, self_employment_income > 0],
            # Second arg: list of values to return if the corresponding condition is True
            [p.new, p.self_employed],
            # Third arg: default value to return if none of the conditions are True
            default=p.not_self_employed,
        )
        # Multiply earned income by percent deduction.
        return spm_unit.sum(earned_income * percent)
