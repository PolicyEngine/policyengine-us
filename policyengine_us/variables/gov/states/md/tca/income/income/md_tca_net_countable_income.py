from policyengine_us.model_api import *


class md_tca_net_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA net countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    def formula(spm_unit, period, parameters):
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        earnings_deduction = spm_unit("md_tca_earnings_deduction", period)
        childcare_deduction = spm_unit("md_tca_childcare_deduction", period)
        # Apply deductions to earned income only, then add unearned
        countable_earned = max_(
            gross_earned - earnings_deduction - childcare_deduction,
            0,
        )
        return countable_earned + gross_unearned
