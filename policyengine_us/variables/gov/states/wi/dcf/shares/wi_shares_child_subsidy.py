from policyengine_us.model_api import *


class wi_shares_child_subsidy(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Wisconsin Shares per-child subsidy"
    definition_period = MONTH
    defined_for = "wi_shares_eligible_child"
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=150",
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=155",
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=173",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.hours
        # The per-child subsidy is the least of the hourly maximum times the
        # monthly subsidized hours, the provider's monthly price, and the
        # monthly maximum rate (Section 18.5). pre_subsidy_childcare_expenses
        # is an annual amount read with the bare monthly period, so Core
        # auto-divides it to a monthly value.
        hourly_max = person("wi_shares_hourly_max_rate", period)
        subsidized_hours = person("wi_shares_monthly_subsidized_hours", period)
        provider_price = person("pre_subsidy_childcare_expenses", period)
        monthly_max = person("wi_shares_monthly_max_rate", period)
        uncapped_subsidy = hourly_max * subsidized_hours
        base_subsidy = min_(uncapped_subsidy, min_(provider_price, monthly_max))
        # Children needing more than 50 weekly hours of care receive a weekly
        # add-on for the hours above 50 (up to 75) at the hourly maximum,
        # converted to a monthly amount and added after the capped-subsidy
        # comparison (Sections 16.1.1 and 18.5).
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        addon_weekly_hours = min_(
            max_(weekly_hours - p.above_full_time_threshold, 0),
            p.above_full_time_cap - p.above_full_time_threshold,
        )
        # Monthly hours round up to the whole hour per the program-wide
        # conversion convention (Section 16.1.1); the handbook has no worked
        # add-on example, so the round-up here is inferred.
        addon_monthly_hours = np.ceil(addon_weekly_hours * p.weeks_per_month)
        addon = addon_monthly_hours * hourly_max
        # Each child's share of the assistance group copayment is
        # proportional to their copayment hours (Section 18.2). The
        # denominator is the unit's summed per-child capped hours, which
        # equals the assistance group's capped copayment hours except for
        # groups with more than five children, where the proportional shares
        # still allocate exactly the group copayment.
        assistance_group_copay = person.spm_unit("wi_shares_copay", period)
        copay_hours = person("wi_shares_copay_hours", period)
        unit_copay_hours = person.spm_unit.sum(copay_hours)
        copay_share = np.divide(
            assistance_group_copay * copay_hours,
            unit_copay_hours,
            out=np.zeros_like(assistance_group_copay),
            where=unit_copay_hours > 0,
        )
        # If the copayment share equals or exceeds the subsidy, no subsidy is
        # paid for the child, but the family remains eligible
        # (Section 18.2.2).
        return max_(base_subsidy + addon - copay_share, 0)
