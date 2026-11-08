from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parameter_instant import (
    co_ccap_parameter_instant,
)

# With no days of care reported, assume care on each weekday. This is an
# imputation, not a rule, so it is not a parameter.
WEEKDAYS_PER_WEEK = 5


class co_ccap_full_time_equivalent_units(Variable):
    value_type = float
    entity = Person
    label = "Colorado Child Care Assistance Program full-time equivalent units of care per month"
    documentation = (
        "A child's monthly units of care, with each part-time unit counted as "
        "0.55 of a full-time unit. A day of care of unknown length counts as "
        "one full-time unit, and a child with no reported days is assumed to "
        "attend each weekday."
    )
    reference = (
        # PDF pages 10, 85, 119
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=10",
    )
    definition_period = MONTH
    defined_for = "co_ccap_child_in_care"

    def formula(person, period, parameters):
        instant_str = co_ccap_parameter_instant(period)
        p = parameters(instant_str).gov.states.co.ccap.parent_fee.part_time
        year = period.this_year
        daily_hours = person("childcare_hours_per_day", year)
        # Zero is also the input default for unknown hours.
        daily_units = where(
            daily_hours > 0,
            p.full_time_equivalent_units.calc(daily_hours, right=True),
            1,
        )
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR
        monthly_days = person("childcare_attending_days_per_month", year)
        weekly_days = person("childcare_days_per_week", year)
        days = select(
            [monthly_days > 0, weekly_days > 0],
            [monthly_days, weekly_days * weeks_per_month],
            default=WEEKDAYS_PER_WEEK * weeks_per_month,
        )
        return daily_units * days
