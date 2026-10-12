from policyengine_us.model_api import *


class medicare_part_a_premium(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part A premium"
    unit = USD
    definition_period = YEAR
    defined_for = "medicare_enrolled"
    reference = "https://www.medicare.gov/basics/costs/medicare-costs"
    documentation = (
        "Annual Medicare Part A premium paid out of pocket by the enrollee, "
        "net of Medicare Savings Program coverage."
    )

    def formula(person, period, parameters):
        base_premium = person("base_part_a_premium", period)
        msp_coverage = person("msp_part_a_premium_coverage", period)
        return max_(base_premium - msp_coverage, 0)
