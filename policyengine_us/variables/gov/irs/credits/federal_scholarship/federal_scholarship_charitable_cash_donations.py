from policyengine_us.model_api import *


class federal_scholarship_charitable_cash_donations(Variable):
    value_type = float
    entity = Person
    label = "Charitable cash donations after scholarship credit exclusions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/us/usc/t26/s25F/",
        # Proposed 1.25F-2(f) excludes credit carried forward as well as used.
        "https://www.govinfo.gov/content/pkg/FR-2026-10-02/html/2026-20277.htm",
        "https://www.ecfr.gov/current/title-26/section-1.170A-1#p-1.170A-1(h)(3)",
    )

    def formula(person, period, parameters):
        cash = person("resolved_charitable_cash_donations_50_pct", period)
        qualified = person(
            "federal_scholarship_qualified_contributions_eligible", period
        )
        excluded = add(
            person,
            period,
            [
                "federal_scholarship_tax_credit_person",
                "federal_scholarship_state_credit_deduction_reduction",
            ],
        )
        return max_(cash - min_(qualified, max_(excluded, 0)), 0)
