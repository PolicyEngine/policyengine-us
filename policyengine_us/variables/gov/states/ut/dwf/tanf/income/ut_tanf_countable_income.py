from policyengine_us.model_api import *


class ut_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah Family Employment Program countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://adminrules.utah.gov/public/rule/R986-200/Current%20Rules"
    )
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Countable income = gross_earned - deductions + gross_unearned
        person = spm_unit.members
        gross_earned = spm_unit.sum(person("tanf_gross_earned_income", period))
        deduction = spm_unit("ut_tanf_earned_income_deduction", period)
        countable_earned = max_(gross_earned - deduction, 0)
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        return countable_earned + gross_unearned
