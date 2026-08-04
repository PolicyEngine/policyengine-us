from policyengine_us.model_api import *


class mn_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Minnesota CCAP countable annual income"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/rules/3400.0170/",
        "https://www.revisor.mn.gov/statutes/cite/256P.06",
    )

    def formula(spm_unit, period, parameters):
        # Annual gross income (earned counted gross, before payroll deductions)
        # less allowable deductions, used for both the income-eligibility test
        # and the copayment lookup. Flooring the result at zero matches the
        # labor-supply rule and prevents net losses from inflating the benefit.
        earned = add(spm_unit, period, ["mn_ccap_gross_earned_income"])
        unearned = add(spm_unit, period, ["mn_ccap_gross_unearned_income"])
        deductions = add(spm_unit, period, ["mn_ccap_income_deductions"])
        return max_(earned + unearned - deductions, 0)
