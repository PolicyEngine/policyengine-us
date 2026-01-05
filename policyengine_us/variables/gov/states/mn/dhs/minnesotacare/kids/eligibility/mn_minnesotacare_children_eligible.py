from policyengine_us.model_api import *


class mn_minnesotacare_children_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for MinnesotaCare for children"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = [
        "https://www.revisor.mn.gov/statutes/cite/256L.04",
        "https://www.dhs.state.mn.us/main/groups/publications/documents/pub/mndhs-068276.pdf",
    ]
    documentation = """
    MinnesotaCare provides state-funded health coverage for undocumented
    children under age 18 with family income at or below 200% FPL.

    The 2023 Minnesota Legislature expanded MinnesotaCare to include
    undocumented individuals, with coverage beginning January 1, 2025.
    Per subdivision 10(c), undocumented noncitizens age 18 or older have
    restricted eligibility (only those enrolled as of June 15, 2025, and
    losing eligibility January 1, 2026). Children under 18 continue to
    be eligible.

    Per Minnesota Statutes 256L.04 subdivision 10:
    "Notwithstanding subdivisions 1 and 7, eligible persons include families
    and individuals who are ineligible for medical assistance by reason of
    immigration status and who have incomes equal to or less than 200 percent
    of federal poverty guidelines."
    """

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mn.dhs.minnesotacare.kids.eligibility

        # Program must be in effect (started January 1, 2025)
        in_effect = p.in_effect

        # Must be under age 18 per subdivision 10(c)
        age = person("age", period)
        age_eligible = age < p.age_limit

        # Must meet income requirements (at or below 200% FPL)
        income_eligible = person(
            "mn_minnesotacare_children_income_eligible", period
        )

        # Must be undocumented (ineligible for federal programs)
        immigration_eligible = person(
            "mn_minnesotacare_children_immigration_status_eligible", period
        )

        return (
            in_effect & age_eligible & income_eligible & immigration_eligible
        )
