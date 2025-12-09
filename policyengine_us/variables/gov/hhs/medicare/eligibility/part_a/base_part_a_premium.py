from policyengine_us.model_api import *


class base_part_a_premium(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part A Base Premium"
    unit = USD
    documentation = (
        "Annual Medicare Part A premium. Most people (99%) qualify for "
        "premium-free Part A with 40+ quarters of Medicare-covered employment. "
        "Those with 30-39 quarters pay a reduced premium, and those with "
        "fewer than 30 quarters pay the full premium."
    )
    definition_period = YEAR
    reference = "https://www.cms.gov/newsroom/fact-sheets/2025-medicare-parts-b-premiums-and-deductibles"
    defined_for = "is_medicare_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.part_a
        quarters_covered = person("medicare_quarters_of_coverage", period)

        premium_free_part_a = person("is_premium_free_part_a", period)
        quarters_above_reduced_premium_threshold = (
            quarters_covered >= p.reduced_premium_quarters_threshold
        )
        premium_amount = where(
            quarters_above_reduced_premium_threshold,
            p.reduced_premium,
            p.full_premium,
        )
        return where(premium_free_part_a, 0, premium_amount) * MONTHS_IN_YEAR
