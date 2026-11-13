from policyengine_us.model_api import *


class nd_ccap_child_in_care(Variable):
    value_type = bool
    entity = Person
    label = "North Dakota CCAP person attends child care"
    definition_period = MONTH
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(person, period, parameters):
        # Reported care days or hours establish participation independently
        # of the missing-hours pricing fallback.
        year = period.this_year
        return (
            (person("childcare_hours_per_week", year) > 0)
            | (person("childcare_hours_per_day", year) > 0)
            | (person("childcare_attending_days_per_month", year) > 0)
            | (person("childcare_days_per_week", year) > 0)
        )
