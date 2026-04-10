from policyengine_us.model_api import *


class medicare_part_b_premiums(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premiums"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        enrolled = person("medicare_enrolled", period)
        gross_premium = person("income_adjusted_part_b_premium", period)
        msp_coverage = person("msp_part_b_premium_coverage", period)
        return max_(where(enrolled, gross_premium, 0) - msp_coverage, 0)
