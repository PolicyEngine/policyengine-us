from policyengine_us.model_api import *


class wa_eceap_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Age-eligible for Washington ECEAP"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.505",
        "https://app.leg.wa.gov/WAC/default.aspx?cite=110-425-0080",
    )

    def formula(person, period, parameters):
        # RCW 43.216.505(4) requires a child to be at least 3 by August 31 of
        # the school year and not yet kindergarten-age. WAC 110-425-0080
        # extends eligibility through the school year for a child who enrolls
        # at age 4 and turns 5 mid-year. PolicyEngine evaluates age annually
        # without an Aug-31 anchor, so we take the generous reading and treat
        # ages 3-5 as eligible to capture the mid-year carry-over case.
        age = person("age", period)
        p = parameters(period).gov.states.wa.dcyf.eceap
        return p.age_range.calc(age)
