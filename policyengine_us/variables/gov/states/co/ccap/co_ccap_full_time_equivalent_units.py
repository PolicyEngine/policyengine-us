from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_care_hours_per_day import (
    WEEKDAYS_PER_WEEK,
)


class co_ccap_full_time_equivalent_units(Variable):
    value_type = float
    entity = Person
    label = "Colorado Child Care Assistance Program full-time equivalent units of care per month"
    documentation = (
        "A child's monthly units of care, with each part-time unit counted as "
        "0.55 of a full-time unit. A day of care of unknown length counts as "
        "one full-time unit. Days of care come from the larger of the weekly "
        "schedule (days a week times 52 / 12) and attending days a month, and "
        "a child with neither attends each weekday."
    )
    reference = (
        # 8 CCR 1403-1 3.103(ZZ), 3.124(U) and (V), and 3.130(C) and (F), PDF
        # pages 10, 85 and 119-120: full-time equivalent units, part-time
        # fees, daily units and drop-in days.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=10",
    )
    definition_period = MONTH
    defined_for = "co_ccap_child_in_care"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ccap.parent_fee.part_time
        year = period.this_year
        daily_hours = person("co_ccap_care_hours_per_day", period)
        # Zero is also the input default for unknown hours.
        daily_units = where(
            daily_hours > 0,
            p.full_time_equivalent_units.calc(daily_hours, right=True),
            1,
        )
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR
        # Counties assess the fee on the authorized care schedule (3.124(V)),
        # and attending days above it count the drop-in days a county may pay
        # (3.130(F)).
        weekly_days = person("childcare_days_per_week", year)
        attending_days = person("childcare_attending_days_per_month", year)
        days = max_(weekly_days * weeks_per_month, attending_days)
        default_days = WEEKDAYS_PER_WEEK * weeks_per_month
        return daily_units * where(days > 0, days, default_days)
