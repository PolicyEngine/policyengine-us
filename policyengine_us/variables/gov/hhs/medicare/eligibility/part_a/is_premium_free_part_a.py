from policyengine_us.model_api import *


class is_premium_free_part_a(Variable):
    value_type = bool
    entity = Person
    label = "Qualifies for premium-free Part A"
    documentation = (
        "Whether the person qualifies for premium-free Medicare Part A "
        "based on having 40 or more quarters of Medicare-covered employment. "
        "Approximately 99% of Medicare beneficiaries qualify for premium-free Part A."
    )
    definition_period = YEAR
    reference = (
        "https://www.medicare.gov/basics/costs/medicare-costs/part-a-costs"
    )
    defined_for = "is_medicare_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.part_a
        quarters = person("medicare_quarters_of_coverage", period)
        return quarters >= p.premium_free_quarters_threshold
