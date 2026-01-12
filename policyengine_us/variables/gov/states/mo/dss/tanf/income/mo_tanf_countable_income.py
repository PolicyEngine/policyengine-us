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
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        deductions = spm_unit("mo_tanf_earned_income_deductions", period)
        countable_earned = max_(gross_earned - deductions, 0)
        return countable_earned + gross_unearned
