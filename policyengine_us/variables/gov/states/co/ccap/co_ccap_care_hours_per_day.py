from policyengine_us.model_api import *

# Without a schedule, the model reads a five-day week of care. It imputes
# this, so the number stays out of the parameters.
WEEKDAYS_PER_WEEK = 5


class co_ccap_care_hours_per_day(Variable):
    value_type = float
    entity = Person
    label = "Colorado Child Care Assistance Program hours of care a day"
    unit = "hour"
    documentation = (
        "A child's hours of care a day: the reported daily hours, or weekly "
        "hours spread over the child's days of care in a week. Zero means the "
        "model has no hours for the child."
    )
    reference = (
        # 8 CCR 1403-1 3.130(C), PDF page 119: units of care follow hours a day.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=119",
    )
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        year = period.this_year
        daily_hours = person("childcare_hours_per_day", year)
        weekly_hours = person("childcare_hours_per_week", year)
        days_per_week = person("childcare_days_per_week", year)
        attending_days = person("childcare_attending_days_per_month", year)
        # co_ccap_full_time_equivalent_units takes the same larger day count.
        reported_days = max_(
            days_per_week, attending_days * MONTHS_IN_YEAR / WEEKS_IN_YEAR
        )
        days_in_a_week = where(reported_days > 0, reported_days, WEEKDAYS_PER_WEEK)
        return where(daily_hours > 0, daily_hours, weekly_hours / days_in_a_week)
