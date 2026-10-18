from policyengine_us.model_api import *


class self_employed_health_insurance_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Self-employed health insurance ALD for each person"
    unit = USD
    documentation = (
        "Personal above-the-line deduction for self-employed health insurance "
        "premiums, including eligible long-term care premiums (Form 7206 "
        "lines 1 to 3)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l",
        "https://www.irs.gov/pub/irs-prior/f7206--2024.pdf#page=1",  # Lines 1-3
    )

    def formula(person, period, parameters):
        earnings = max_(0, person("total_self_employment_income", period))
        # Line 3: health insurance premiums (line 1) plus eligible long-term
        # care premiums (line 2).
        premiums = add(
            person,
            period,
            [
                "self_employed_health_insurance_premiums",
                "self_employed_long_term_care_premiums",
            ],
        )
        return min_(earnings, premiums)
