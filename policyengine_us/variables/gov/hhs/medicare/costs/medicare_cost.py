from policyengine_us.model_api import *


class medicare_cost(Variable):
    value_type = float
    entity = Person
    label = "Medicare cost"
    documentation = (
        "Annual value of Medicare benefits received. Calculated as total "
        "Medicare spending on behalf of the beneficiary, which covers Parts A "
        "through D, minus the premiums that finance it: the Part A premium, "
        "the gross Part B premium and the expected Part D premium. "
        "This represents the net benefit value of Medicare coverage."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.cms.gov/about-cms/what-we-do/medicare",
        "https://www.cms.gov/oact/tr/2026#page=116",
    )
    defined_for = "medicare_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).calibration.gov.hhs.medicare
        # Total Medicare spending on behalf of beneficiary
        per_capita_spending = p.per_capita_cost

        # Premium offsets to Medicare program cost. Use the enrollment-gated
        # gross Part B premium before MSP offsets so MSP support does not
        # inflate Medicare's value.
        part_a_premium = person("base_part_a_premium", period)
        part_b_premium = person("gross_medicare_part_b_premium_if_enrolled", period)
        # The spending includes Part D, which enrollee premiums partly finance.
        # No variable records Part D enrollment, so subtract the expected
        # Part D premium: the Part D enrollment share times the premium per
        # Part D enrollee plus the person's income-related adjustment.
        part_d_irmaa = person("income_adjusted_part_d_premium_surcharge", period)
        part_d_premium = p.part_d.enrollment_share * (
            p.part_d.premiums_per_enrollee + part_d_irmaa
        )
        total_premiums = part_a_premium + part_b_premium + part_d_premium

        # Net benefit = spending - premiums
        return max_(per_capita_spending - total_premiums, 0)
