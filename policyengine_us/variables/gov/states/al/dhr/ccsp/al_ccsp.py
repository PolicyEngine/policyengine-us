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

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.al.dhr.ccsp

        # Per-child weekly maximum rate and the family weekly copay
        # split equally across eligible children.
        weekly_rate = person("al_ccsp_maximum_weekly_rate", period)
        is_eligible_child = person("al_ccsp_eligible_child", period)
        in_care = person("childcare_hours_per_week", period.this_year) > 0
        is_paying_child = is_eligible_child & in_care
        n_paying = spm_unit.sum(is_paying_child)

        weekly_family_copay = (
            spm_unit("al_ccsp_weekly_copay_per_child", period) * n_paying
        )
        # Apply copay waivers consistently with al_ccsp_copay.
        p_elig = p.eligibility
        is_disabled = person("is_disabled", period.this_year)
        age = person("age", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        has_disabled_child = spm_unit.any(
            is_disabled & is_dependent & (age < p_elig.disabled_child_age_limit)
        )
        is_head_start = person("is_enrolled_in_head_start", period.this_year)
        has_head_start_child = spm_unit.any(is_head_start)
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        copay_waived = has_disabled_child | has_head_start_child | has_foster_child
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

        # Convert weekly to monthly using AL's regulatory 4.333 factor.
        weeks_to_months = p.income.weeks_to_months
        per_child_monthly_subsidy = (
            per_child_weekly_subsidy * weeks_to_months * is_paying_child
        )
        return spm_unit.sum(per_child_monthly_subsidy)
