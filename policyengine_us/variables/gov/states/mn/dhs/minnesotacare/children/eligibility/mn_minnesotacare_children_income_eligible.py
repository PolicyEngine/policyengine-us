from policyengine_us.model_api import *


class mn_minnesotacare_children_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets MinnesotaCare for children income eligibility"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = [
        "https://www.revisor.mn.gov/statutes/cite/256L.04",
    ]
    documentation = """
    MinnesotaCare for children uses MAGI-based income at or below 200% FPL.
    Per Minnesota Statutes 256L.04 subdivision 1, children with family income
    at or below 200 percent of federal poverty guidelines are eligible.
    """

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mn.dhs.minnesotacare.children.eligibility

        # Use MAGI-based income level (as fraction of FPL)
        income_level = person("medicaid_income_level", period)

        # Eligible if at or below 200% FPL
        return income_level <= p.income_limit
