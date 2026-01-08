from policyengine_us.model_api import *


class wa_apple_health_expansion_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Washington Apple Health Expansion income eligibility"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = [
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-525-0300",
        "https://www.hca.wa.gov/assets/free-or-low-cost/income-standards.pdf",
    ]
    documentation = """
    Washington Apple Health Expansion uses MAGI-based income at or below
    138% FPL. The 5% disregard is already built into the threshold.
    """

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.wa.hca.apple_health.expansion.eligibility

        # Use MAGI-based income level (as fraction of FPL)
        income_level = person("medicaid_income_level", period)

        # Eligible if at or below 138% FPL
        return income_level <= p.income_limit
