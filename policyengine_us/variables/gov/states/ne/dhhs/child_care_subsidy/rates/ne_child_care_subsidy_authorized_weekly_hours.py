from policyengine_us.model_api import *


class ne_child_care_subsidy_authorized_weekly_hours(Variable):
    value_type = float
    entity = Person
    unit = "hour"
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy authorized weekly care hours"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=16",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.activity
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        daily_hours = min_(
            person("childcare_hours_per_day", period.this_year),
            p.max_daily_hours,
        )
        days_per_week = person("childcare_days_per_week", period.this_year)
        return min_(
            min_(weekly_hours, daily_hours * days_per_week),
            p.max_weekly_hours,
        )
