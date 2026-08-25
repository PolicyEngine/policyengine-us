from policyengine_us.model_api import *


class medicare_quarters_of_coverage(Variable):
    value_type = int
    entity = Person
    label = "Medicare quarters of coverage"
    documentation = (
        "Number of quarters of Social Security-covered employment. "
        "40 quarters required for premium-free Part A. Defaults to 40 "
        "because survey microdata does not observe work-history quarters "
        "and about 99% of beneficiaries qualify for premium-free Part A; "
        "without this default, microsimulation would charge every enrollee "
        "the full Part A premium."
    )
    default_value = 40
    definition_period = YEAR
