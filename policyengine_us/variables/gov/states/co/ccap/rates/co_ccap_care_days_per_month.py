from policyengine_us.model_api import *

# Without a schedule, read a five-day week of care.
DEFAULT_DAYS_PER_WEEK = 5


class co_ccap_care_days_per_month(Variable):
    value_type = float
    entity = Person
    unit = "day"
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program days of care a month"
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.130(C), PDF page 119: daily rates.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=119",
        # 3.130(E) and (F), PDF pages 119 and 120: paid absences and drop-in
        # days.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=120",
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
        scheduled_days = days_per_week * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        days = max_(scheduled_days, attending_days)
        default_days = DEFAULT_DAYS_PER_WEEK * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        return where(days > 0, days, default_days)
