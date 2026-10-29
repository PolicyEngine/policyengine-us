from policyengine_us.model_api import *


class self_employed_health_insurance_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Self-employed health insurance ALD for each person"
    unit = USD
    documentation = (
        "Personal above-the-line deduction for self-employed health insurance "
        "premiums: the smaller of the premiums and the earned income from the "
        "business under which the plan is established (Form 7206 line 14). "
        "The premiums exclude qualified long-term care insurance (line 2), "
        "which the model does not include in self-employed premiums."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l",
        "https://www.irs.gov/pub/irs-prior/f7206--2023.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/i1040gi--2022.pdf#page=89",
    )

    def formula(person, period, parameters):
        premiums = person("self_employed_health_insurance_premiums", period)
        earned_income_limit = person(
            "self_employed_health_insurance_earned_income_limit", period
        )
        return min_(premiums, earned_income_limit)
