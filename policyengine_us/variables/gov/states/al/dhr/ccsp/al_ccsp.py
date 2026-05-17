from policyengine_us.model_api import *


class al_ccsp(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama Child Care Subsidy Program benefit amount"
    definition_period = MONTH
    defined_for = "al_ccsp_eligible"
    reference = (
        "Alabama CCDF State Plan 2025-2027, Section 3.1",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=40",
    )

    def formula(spm_unit, period):
        person = spm_unit.members

        weekly_rate = person("al_ccsp_maximum_weekly_rate", period)
        is_eligible_child = person("al_ccsp_eligible_child", period)
        in_care = person("childcare_hours_per_week", period.this_year) > 0
        is_paying_child = is_eligible_child & in_care
        n_paying = spm_unit.sum(is_paying_child)

        weekly_family_copay = (
            spm_unit("al_ccsp_weekly_copay_per_child", period) * n_paying
        )
        copay_waived = spm_unit("al_ccsp_copay_waived", period)
        weekly_family_copay = where(copay_waived, 0, weekly_family_copay)

        per_child_weekly_copay = where(
            n_paying > 0, weekly_family_copay / where(n_paying > 0, n_paying, 1), 0
        )
        per_child_weekly_copay_broadcast = spm_unit.project(per_child_weekly_copay)

        # Per-child weekly pre-subsidy charge from annual expenses.
        annual_expense = person("pre_subsidy_childcare_expenses", period.this_year)
        weekly_expense = annual_expense / WEEKS_IN_YEAR

        # Subsidy = max(0, min(charge, max_rate) - per-child copay).
        capped_charge = min_(weekly_expense, weekly_rate)
        per_child_weekly_subsidy = max_(
            capped_charge - per_child_weekly_copay_broadcast, 0
        )

        per_child_monthly_subsidy = (
            per_child_weekly_subsidy
            * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
            * is_paying_child
        )
        return spm_unit.sum(per_child_monthly_subsidy)
