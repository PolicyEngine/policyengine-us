from policyengine_us.model_api import *


class nd_tanf_time_limited_percentage_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota TANF time limited percentage deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40019/400_19_05.htm",
        "https://nd.gov/dhs/policymanuals/40019/Archive%20Documents/2016%20-%20ML3482/400_19_145_15%20ML%203482.htm",
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.tanf.income.deductions
        # Per 400-19-05: TLP disregard is applied to earned income AFTER
        # the Standard Employment Expense Allowance
        # NOTE: TLP operates on a 13-month cycle and decreases over time.
        # PolicyEngine cannot track this, so we apply the 50% rate assuming
        # the household is in the first 6 months of the cycle.
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        standard_expense = spm_unit(
            "nd_tanf_standard_employment_expense", period
        )
        earned_after_expense = max_(gross_earned - standard_expense, 0)
        return earned_after_expense * p.time_limited_percentage.rate
