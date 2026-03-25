from policyengine_us.model_api import *


class wa_apple_health_kids_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Washington Apple Health for Kids income eligibility"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = [
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-505-0100",
        "https://www.hca.wa.gov/assets/free-or-low-cost/income-standards.pdf",
    ]
    documentation = """
    Washington Apple Health for Kids uses MAGI-based income with the 5%
    disregard already built into published thresholds. Maximum eligibility
    is at 317% FPL.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.hca.apple_health.kids.income_limit

        # Use MAGI-based income level (as fraction of FPL)
        income_level = person("medicaid_income_level", period)

        # Eligible if at or below Tier 2 maximum (317% FPL)
        return income_level <= p.tier_2
