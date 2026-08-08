from policyengine_us.model_api import *


class ne_child_care_subsidy_paid_days(Variable):
    value_type = float
    entity = Person
    unit = "day"
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy paid days"
    defined_for = "ne_child_care_subsidy_provider_eligible"
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=23",
        "https://dhhs.ne.gov/Documents/CC-Subsidy-Provider-Booklet.pdf#page=32",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.attendance
        reported_days = person("childcare_attending_days_per_month", period.this_year)
        absence_days = clip(
            person("ne_child_care_subsidy_approved_absence_days", period),
            0,
            p.max_absence_days,
        )
        return max_(reported_days, 0) + absence_days
