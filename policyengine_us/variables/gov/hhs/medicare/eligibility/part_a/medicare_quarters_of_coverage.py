from policyengine_us.model_api import *


class medicare_quarters_of_coverage(Variable):
    value_type = int
    entity = Person
    label = "Medicare quarters of coverage"
    documentation = (
        "Number of quarters of Medicare-covered employment. Most people have "
        "40+ quarters and qualify for premium-free Part A. Those with 30-39 "
        "quarters pay a reduced premium, and those with fewer than 30 quarters "
        "pay the full premium."
    )
    definition_period = YEAR

    adds = "gov.hhs.medicare.part_a.default_quarters_of_coverage"
