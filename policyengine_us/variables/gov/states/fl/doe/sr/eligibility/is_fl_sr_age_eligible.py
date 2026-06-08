from policyengine_us.model_api import *


class is_fl_sr_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Age-eligible for the Florida School Readiness program"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://www.flsenate.gov/laws/statutes/2024/1002.87",
        "https://flrules.elaws.us/fac/6m-4.200",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.fl.doe.sr.eligibility
        age = person("age", period.this_year)
        return age < p.child_age_limit
