from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_care_hours_per_day import (
    WEEKDAYS_PER_WEEK,
)


class co_ccap_care_days_per_month(Variable):
    value_type = float
    entity = Person
    unit = "day"
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program days of care a month"
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.130(C), (E) and (F), PDF pages 119-120: daily rates,
        # paid absences and drop-in days.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=119",
    )

    def formula(person, period, parameters):
        days_per_week = person("childcare_days_per_week", period.this_year)
        attending_days = person("childcare_attending_days_per_month", period.this_year)
        # Counties pay licensed providers at least three or four absences a
        # month within an authorized schedule, and through a county rate plan
        # may pay more, along with holidays and hold slots (3.130(E)). The
        # model carries no county's absence policy, so the scheduled days set
        # the most a county may pay. Attending days above the schedule count
        # the drop-in days a county may pay (3.130(F)).
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR
        days = max_(days_per_week * weeks_per_month, attending_days)
        # Without a schedule, read a five-day week of care.
        default_days = WEEKDAYS_PER_WEEK * weeks_per_month
        # A county pays for at most every day of the month.
        return min_(where(days > 0, days, default_days), period.size_in_days)
