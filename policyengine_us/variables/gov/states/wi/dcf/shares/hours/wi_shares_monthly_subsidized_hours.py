from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dcf.shares.hours.wi_shares_time_category import (
    WISharesTimeCategory,
)


class wi_shares_monthly_subsidized_hours(Variable):
    value_type = float
    entity = Person
    unit = "hour"
    label = "Wisconsin Shares monthly subsidized hours"
    definition_period = MONTH
    defined_for = "wi_shares_eligible_child"
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=155",
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=173",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.hours
        # The subsidy calculation uses fixed conversion hours, not the child's
        # actual authorized hours: 30 weekly hours for part-time and 35 for
        # full-time authorizations, times 4.348125 weeks per month, rounded up
        # to 131 and 153 monthly hours (Section 18.5).
        time_category = person("wi_shares_time_category", period)
        full_time = time_category == WISharesTimeCategory.FULL_TIME
        conversion_hours = where(
            full_time,
            p.full_time_weekly_conversion,
            p.part_time_weekly_conversion,
        )
        monthly_hours = np.ceil(conversion_hours * p.weeks_per_month)
        # A child with no hours of care has no authorization.
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        return where(weekly_hours > 0, monthly_hours, 0)
