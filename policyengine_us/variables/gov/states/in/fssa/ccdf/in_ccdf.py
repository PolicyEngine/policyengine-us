from policyengine_us.model_api import *


class in_ccdf(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Indiana CCDF benefit amount"
    definition_period = MONTH
    defined_for = "in_ccdf_eligible"
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=39"
    )

    def formula(spm_unit, period, parameters):
        # The subsidy is the lesser of the provider charge and the maximum
        # reimbursement rate, minus the weekly copay converted to monthly.
        # The family pays directly for any charge above the reimbursement rate.
        maximum_monthly_rate = add(spm_unit, period, ["in_ccdf_max_rate_per_child"])
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expenses = min_(pre_subsidy_childcare_expenses, maximum_monthly_rate)
        weekly_copay = spm_unit("in_ccdf_copay", period)
        monthly_copay = weekly_copay * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        return max_(capped_expenses - monthly_copay, 0)
