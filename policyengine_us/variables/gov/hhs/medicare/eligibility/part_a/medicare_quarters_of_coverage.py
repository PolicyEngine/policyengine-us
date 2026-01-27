from policyengine_us.model_api import *


class medicare_quarters_of_coverage(Variable):
    value_type = int
    entity = Person
    label = "Medicare quarters of coverage"
    documentation = (
        "Number of quarters of Social Security-covered employment. "
        "40 quarters required for premium-free Part A."
    )
    definition_period = YEAR
