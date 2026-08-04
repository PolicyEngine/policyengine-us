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
        # reimbursement rate, minus the monthly copay.
        # The family pays directly for any charge above the reimbursement rate.
        # The expense cap pools the per-child maximum rates across the unit
        # (the MA / RI / AK child care subsidy convention); childcare expenses
        # are a single SPM-unit input, so we don't cap each child's charges
        # separately at the moment.
        maximum_monthly_rate = add(spm_unit, period, ["in_ccdf_max_rate_per_child"])
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expenses = min_(pre_subsidy_childcare_expenses, maximum_monthly_rate)
        monthly_copay = spm_unit("in_ccdf_copay", period)
        return max_(capped_expenses - monthly_copay, 0)
