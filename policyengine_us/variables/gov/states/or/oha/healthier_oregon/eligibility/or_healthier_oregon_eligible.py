from policyengine_us.model_api import *


class or_healthier_oregon_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Oregon Healthier Oregon"
    definition_period = YEAR
    defined_for = StateCode.OR
    reference = (
        "https://www.oregon.gov/oha/hsd/ohp/pages/healthier-oregon.aspx",
        "https://olis.oregonlegislature.gov/liz/2021R1/Downloads/MeasureDocument/HB3352/Enrolled",
    )

    def formula(person, period, parameters):
        p = (
            parameters(period)
            .gov.states["or"]
            .oha.healthier_oregon.eligibility
        )

        # Program must be in effect
        in_effect = p.in_effect

        # Must have non-federally-eligible immigration status
        immigration_eligible = person(
            "or_healthier_oregon_immigration_status_eligible", period
        )

        # Must meet income requirements
        income_eligible = person("or_healthier_oregon_income_eligible", period)

        return in_effect & immigration_eligible & income_eligible
