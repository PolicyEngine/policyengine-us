from policyengine_us.model_api import *


class eligible_long_term_care_premiums(Variable):
    value_type = float
    entity = Person
    label = "Eligible long-term care premiums"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/213#d_1_D",
        "https://www.law.cornell.edu/uscode/text/26/213#d_10",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/p502--2018.pdf#page=11",
    )
    documentation = (
        "Premiums for a person's qualified long-term care insurance contract "
        "that count as medical care under 26 U.S.C. 213(d)(1)(D): the "
        "premiums up to the 213(d)(10) limit for the person's age at the end "
        "of the year. The limit applies to each insured person, so "
        "long_term_health_insurance_premiums is recorded on the person the "
        "contract covers. These premiums enter the Schedule A medical "
        "subtotal and, for a self-employed person, the self-employed health "
        "insurance deduction (26 U.S.C. 162(l)(2)(C))."
    )

    def formula(person, period, parameters):
        premiums = person("long_term_health_insurance_premiums", period)
        p = parameters(period).gov.irs.deductions.itemized.medical
        # The limit depends on the age, at the end of the year, of the person
        # for whom the premiums were paid (Schedule A instructions, line 1).
        limit = p.long_term_care_premium_limit.calc(person("age", period), right=True)
        return min_(premiums, limit)
