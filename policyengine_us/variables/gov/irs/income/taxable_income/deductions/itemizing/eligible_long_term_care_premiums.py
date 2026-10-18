from policyengine_us.model_api import *


class eligible_long_term_care_premiums(Variable):
    value_type = float
    entity = Person
    label = "Eligible long-term care premiums"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/213#d_10",
        "https://www.irs.gov/pub/irs-drop/rp-22-38.pdf#page=17",
    )
    documentation = (
        "Long-term care insurance premiums counted as medical care under "
        "26 U.S.C. 213(d)(1)(D): the premiums up to the age-based limit of "
        "213(d)(10), using the person's age as the insured's age. The "
        "computed itemized_medical_expenses does not yet include them."
    )

    def formula(person, period, parameters):
        premiums = person("long_term_health_insurance_premiums", period)
        p = parameters(period).gov.irs.deductions.itemized.medical
        # "40 or less", "more than 40 but not more than 50": band tops.
        limit = p.long_term_care_premium_limit.calc(person("age", period), right=True)
        return min_(premiums, limit)
