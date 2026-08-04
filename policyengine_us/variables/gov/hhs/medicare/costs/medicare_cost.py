from policyengine_us.model_api import *


class medicare_cost(Variable):
    value_type = float
    entity = Person
    label = "Medicare cost"
    documentation = (
        "Annual value of Medicare benefits received. Calculated as total "
        "Medicare spending on behalf of the beneficiary minus premiums paid. "
        "This represents the net benefit value of Medicare coverage."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.cms.gov/medicare"
    defined_for = "medicare_enrolled"

    def formula(person, period, parameters):
        # Total Medicare spending on behalf of beneficiary
        per_capita_spending = parameters(
            period
        ).calibration.gov.hhs.medicare.per_capita_cost

        # Premium offsets to Medicare program cost. Use the enrollment-gated
        # gross Part B premium before MSP offsets so MSP support does not
        # inflate Medicare's value.
        part_a_premium = person("base_part_a_premium", period)
        part_b_premium = person("gross_medicare_part_b_premium_if_enrolled", period)
        total_premiums = part_a_premium + part_b_premium

        # Net benefit = spending - premiums
        return max_(per_capita_spending - total_premiums, 0)
