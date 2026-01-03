from policyengine_us.model_api import *


class nd_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.nd.gov/dhs/policymanuals/40019/400_19_110_20.htm"
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        standard_expense = spm_unit(
            "nd_tanf_standard_employment_expense", period
        )
        tlp_deduction = spm_unit(
            "nd_tanf_time_limited_percentage_deduction", period
        )
        return max_(gross_earned - standard_expense - tlp_deduction, 0)
