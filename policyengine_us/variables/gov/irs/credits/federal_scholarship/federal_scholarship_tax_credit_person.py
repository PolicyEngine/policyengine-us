from policyengine_us.model_api import *


class federal_scholarship_tax_credit_person(Variable):
    value_type = float
    entity = Person
    label = "Current-year Federal Scholarship Tax Credit potential per donor"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/us/usc/t26/s25F/",
        # Proposed 1.25F-2(a)(2), (c)(1): separate donor caps, state offset first.
        "https://www.govinfo.gov/content/pkg/FR-2026-10-02/html/2026-20277.htm",
    )

    def formula_2027_01_01(person, period, parameters):
        p = parameters(period).gov.irs.credits.federal_scholarship
        qualified = person(
            "federal_scholarship_qualified_contributions_eligible", period
        )
        state_credit = max_(person("federal_scholarship_state_tax_credit", period), 0)
        return min_(max_(qualified - state_credit, 0), p.maximum)
