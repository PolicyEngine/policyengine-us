from policyengine_us.model_api import *


class mo_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF countable income after all disregards for Percentage of Need test"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-15/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        gross_earned_income = spm_unit("mo_tanf_gross_earned_income", period)
        unearned_income = spm_unit("mo_tanf_unearned_income", period)
        earned_income_deductions = spm_unit(
            "mo_tanf_earned_income_deductions", period
        )

        # Total income minus all earned income deductions
        total_income = gross_earned_income + unearned_income
        countable_income = total_income - earned_income_deductions

        return max_(countable_income, 0)
