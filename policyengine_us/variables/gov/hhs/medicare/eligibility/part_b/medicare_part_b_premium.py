from policyengine_us.model_api import *


class medicare_part_b_premium(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premium"
    unit = USD
    definition_period = YEAR
    defined_for = "medicare_enrolled"
    reference = "https://www.medicare.gov/your-medicare-costs/part-b-costs"
    documentation = "Annual Medicare Part B premium paid out of pocket by the enrollee, net of Medicare Savings Program coverage."

    def formula(person, period, parameters):
        gross_premium = person("gross_medicare_part_b_premium", period)
        msp_coverage = person("msp_part_b_premium_coverage", period)
        return max_(gross_premium - msp_coverage, 0)
