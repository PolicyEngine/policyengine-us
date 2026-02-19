from policyengine_us.model_api import *


class wa_apple_health_kids_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Washington Apple Health for Kids"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = [
        "https://app.leg.wa.gov/rcw/default.aspx?cite=74.09.470",
        "https://www.hca.wa.gov/free-or-low-cost-health-care/i-need-medical-dental-or-vision-care/children",
    ]
    documentation = """
    Washington Apple Health for Kids provides state-funded Medicaid/CHIP
    coverage for children under 19 regardless of immigration status.
    Coverage is available at different premium tiers based on income.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.hca.apple_health.kids

        # Program must be in effect
        in_effect = p.eligibility.in_effect

        # Must be under age limit (19)
        age = person("age", period)
        age_eligible = age < p.eligibility.age_limit

        # Must meet income requirements
        income_eligible = person(
            "wa_apple_health_kids_income_eligible", period
        )

        # Washington covers children regardless of immigration status
        # No immigration status check needed

        return in_effect & age_eligible & income_eligible
