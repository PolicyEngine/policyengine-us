from policyengine_us.model_api import *


class wa_apple_health_expansion_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Washington Apple Health Expansion"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = [
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-525-0300",
        "https://www.hca.wa.gov/about-hca/programs-and-initiatives/apple-health-medicaid/apple-health-expansion",
    ]
    documentation = """
    Washington Apple Health Expansion provides state-funded coverage for
    adults age 19+ who are ineligible for federally funded Medicaid or
    QHPs with APTC due to immigration status. Income limit is 138% FPL.

    Note: This program has an enrollment cap and is not an entitlement.
    Enrollment closed within 48 hours of launch on June 21, 2024.
    The cap is not modeled here.

    Exclusions:
    - Pregnant individuals (must use pregnancy programs)
    - Qualified immigrants in 5-year bar
    - DACA recipients (status unclear as of January 2026)
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.hca.apple_health.expansion

        # Program must be in effect (launched June 21, 2024)
        in_effect = p.eligibility.in_effect

        # Must be adult (19+)
        age = person("age", period)
        age_eligible = age >= p.eligibility.min_age

        # Must meet income requirements
        income_eligible = person(
            "wa_apple_health_expansion_income_eligible", period
        )

        # Must have eligible immigration status
        immigration_eligible = person(
            "wa_apple_health_expansion_immigration_status_eligible", period
        )

        # Must not be pregnant (pregnant individuals use pregnancy programs)
        is_pregnant = person("is_pregnant", period)

        return (
            in_effect
            & age_eligible
            & income_eligible
            & immigration_eligible
            & ~is_pregnant
        )
