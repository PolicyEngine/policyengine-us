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
    reference = (
        "https://www.cms.gov/medicare/medicare-part-a-b-premiums-deductibles"
    )
    defined_for = "is_medicare_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.part_a
        quarters = person("medicare_quarters_of_coverage", period)

        # Get thresholds from parameters
        premium_free_threshold = p.premium_free_quarters_threshold
        reduced_premium_threshold = p.reduced_premium_quarters_threshold

        # Calculate annual premiums from monthly amounts
        full_premium = p.full_premium * 12
        reduced_premium = p.reduced_premium * 12

        # Return premium based on quarters of coverage
        return where(
            quarters >= premium_free_threshold,
            0,  # Premium-free
            where(
                quarters >= reduced_premium_threshold,
                reduced_premium,  # Reduced premium
                full_premium,  # Full premium
            ),
        )
