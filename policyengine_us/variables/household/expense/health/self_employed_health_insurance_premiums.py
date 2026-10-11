from policyengine_us.model_api import *


class self_employed_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Self-employed health insurance premiums"
    unit = USD
    documentation = (
        "Health insurance premiums that count toward the self-employed health "
        "insurance deduction (Form 7206 line 1). Premiums are left out when "
        "the person or their spouse is eligible for a subsidized employer "
        "plan (26 U.S.C. 162(l)(2)(B)). Premiums are taken as supplied: for a "
        "Marketplace plan, 26 U.S.C. 280C(g) allows no deduction for the part "
        "the premium tax credit pays, and the model does not net the credit "
        "it calculates out of these premiums."
    )
    definition_period = YEAR
    defined_for = "is_self_employed"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l",
        "https://www.irs.gov/pub/irs-prior/f7206--2025.pdf#page=1",  # Line 1
    )

    def formula(person, period, parameters):
        premiums = person("health_insurance_premiums", period)
        employer_plan_eligible = person(
            "self_employed_health_insurance_employer_plan_eligible", period
        )
        return where(employer_plan_eligible, 0, premiums)
