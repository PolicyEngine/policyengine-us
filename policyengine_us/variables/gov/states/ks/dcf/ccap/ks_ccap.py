from policyengine_us.model_api import *


class ks_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Kansas CCAP benefit amount"
    definition_period = MONTH
    defined_for = "ks_ccap_eligible"
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/appendix/c-18_providerratecht.pdf#page=8"
    )

    def formula(spm_unit, period, parameters):
        # KEESM 10200: the per-child benefit is the lesser of the family's actual
        # child care cost and the maximum hourly provider rate times the
        # authorized monthly hours. The total across eligible children is reduced
        # by the family share deduction and floored at zero, then capped at the
        # family's actual child care expenses.
        person = spm_unit.members
        is_eligible_child = person("ks_ccap_eligible_child", period)
        hourly_rate = person("ks_ccap_hourly_rate", period)
        monthly_hours = person("ks_ccap_monthly_hours", period)
        # pre_subsidy_childcare_expenses is YEAR-defined; bare period
        # auto-divides the annual figure to the monthly amount.
        pre_subsidy_per_child = person("pre_subsidy_childcare_expenses", period)
        max_rate = hourly_rate * monthly_hours
        per_child_reimbursement = where(
            is_eligible_child,
            min_(pre_subsidy_per_child, max_rate),
            0,
        )
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        family_share = spm_unit("ks_ccap_family_share", period)
        benefit = max_(total_reimbursement - family_share, 0)
        # Cap at the family's total actual child care expenses (monthly).
        actual_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        return min_(benefit, actual_expenses)
