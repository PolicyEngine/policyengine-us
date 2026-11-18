from policyengine_us.model_api import *


class medicare_part_b_premium_before_buy_in(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premium before the Medicaid buy-in"
    unit = USD
    definition_period = YEAR
    defined_for = "medicare_part_b_enrolled"
    reference = (
        "https://www.ecfr.gov/current/title-42/section-407.42",
        "https://www.law.cornell.edu/uscode/text/42/1395v#d",
    )
    documentation = (
        "Annual Medicare Part B premium a Part B enrollee owes, net of "
        "Medicare Savings Program coverage but before a state's Medicaid "
        "buy-in for SSI recipients. Buy-in coverage starts only once Medicaid "
        "finds the person eligible, so Medicaid eligibility tests count this "
        "premium. Reading it instead of medicare_part_b_premium keeps those "
        "tests from depending on the buy-in they determine."
    )

    def formula(person, period, parameters):
        gross_premium = person("gross_medicare_part_b_premium", period)
        msp_coverage = person("msp_part_b_premium_coverage", period)
        return max_(gross_premium - msp_coverage, 0)
